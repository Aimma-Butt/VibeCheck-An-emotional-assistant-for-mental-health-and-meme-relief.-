import React, { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import "./TrackAndGenerate.css";
import logo from "./assets/VC.png";
import memesHeader from "./assets/memes-header.png";
import memesFooter from "./assets/memes-footer.png";
import AgeDisclaimerMarquee from "./AgeDisclaimerMarquee";


import { auth } from "./firebase";
import { onAuthStateChanged } from "firebase/auth";

const TrackAndGenerate = () => {
  const [text, setText] = useState("");
  const [message, setMessage] = useState("");
  const [entertainment, setEntertainment] = useState(null);
  const [memes, setMemes] = useState([]);
  const [emotion, setEmotion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [shareDropdownIdx, setShareDropdownIdx] = useState(null);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const navigate = useNavigate();
  const audioContainerRef = useRef(null);

  const API_URL = "http://localhost:5000/api";

  const [user, setUser] = useState(null);

  React.useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
    });

    return () => unsubscribe();
  }, []);

  const userMenuRef = React.useRef(null);
  const shareMenuRef = React.useRef(null);

  React.useEffect(() => {
    const handleClickOutside = (event) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setShowUserMenu(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  React.useEffect(() => {
    const handleClickOutsideShare = (event) => {
      if (shareMenuRef.current && !shareMenuRef.current.contains(event.target)) {
        setShareDropdownIdx(null);
      }
    };

    document.addEventListener("mousedown", handleClickOutsideShare);
    return () => document.removeEventListener("mousedown", handleClickOutsideShare);
  }, []);

  React.useEffect(() => {
    localStorage.setItem("trackText", text);
  }, [text]);

  React.useEffect(() => {
    localStorage.setItem("trackMemes", JSON.stringify(memes));
  }, [memes]);

  React.useEffect(() => {
    localStorage.setItem("trackMessage", message);
  }, [message]);

  React.useEffect(() => {
    localStorage.setItem("trackEntertainment", JSON.stringify(entertainment));
  }, [entertainment]);

  React.useEffect(() => {
    localStorage.setItem("trackEmotion", emotion);
  }, [emotion]);

  const handleLogout = () => {
    auth.signOut();
    setUser(null);
    localStorage.removeItem("trackText");
    localStorage.removeItem("trackMemes");
    localStorage.removeItem("trackMessage");
    localStorage.removeItem("trackEntertainment");
    localStorage.removeItem("trackEmotion");
    navigate("/login");
  };

  const analyzeAndGenerate = async (inputText) => {
    const payloadText = (inputText ?? text).trim();
    if (payloadText === "") {
      setError("Please share your thoughts first 😊");
      return;
    }

    setIsLoading(true);
    setError("");
    setMessage("");
    setEntertainment(null);
    setMemes([]);
    setEmotion("");

    try {
      const resp = await fetch(`${API_URL}/analyze-complete`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: payloadText }),
      });
      const data = await resp.json();

      if (resp.ok && data.success) {
        setMessage(data.recommendations || data.message || "");
        setEntertainment(data.entertainment || null);
        setEmotion(data.emotion || "");
        setMemes(data.memes || []);
        document.getElementById("memesSection")?.scrollIntoView({ behavior: "smooth" });
      } else {
        setError(data.error || "Something went wrong. Try again.");
      }
    } catch (err) {
      console.error("Error:", err);
      setError("Failed to connect to server. Make sure backend is running.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleProceed = async () => {
    await analyzeAndGenerate(text);
  };

  const handleVoiceRecording = async () => {
    const btn = document.getElementById("recordBtn");

    if (btn.dataset.recording === "true" && window.mediaRecorder) {
      window.mediaRecorder.stop();
      btn.dataset.recording = "false";
      btn.innerHTML = "🎤 🎙️";
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      const audioChunks = [];
      window.mediaRecorder = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });

        const audioUrl = URL.createObjectURL(audioBlob);
        const audioEl = document.createElement("audio");
        audioEl.controls = true;
        audioEl.src = audioUrl;
        if (audioContainerRef.current) {
          audioContainerRef.current.innerHTML = "";
          audioContainerRef.current.appendChild(audioEl);
        }

        const formData = new FormData();
        formData.append("audio", audioBlob, "recording.webm");

        try {
          setIsLoading(true);
          const response = await fetch(`${API_URL}/transcribe-audio`, {
            method: "POST",
            body: formData,
          });
          const data = await response.json();

          if (response.ok && data.success) {
            if (data.recommendations) setMessage(data.recommendations);
            if (data.entertainment) setEntertainment(data.entertainment);
            if (data.memes) setMemes(data.memes);
            if (data.emotion) setEmotion(data.emotion);
            document.getElementById("memesSection")?.scrollIntoView({ behavior: "smooth" });
          } else {
            alert("Processing failed: " + (data.error || "Unknown error"));
          }
        } catch (error) {
          console.error("Transcription error:", error);
          alert("Failed to transcribe/process audio");
        } finally {
          setIsLoading(false);
        }
      };

      mediaRecorder.start();
      btn.dataset.recording = "true";
      btn.innerHTML = "⏹️";
    } catch (err) {
      alert("Microphone access denied or not supported.");
      console.error(err);
    }
  };

  const handleDownload = async (imageUrl) => {
    try {
      const response = await fetch(imageUrl, { mode: "cors" });
      const blob = await response.blob();

      const blobUrl = URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = blobUrl;

      const filename = imageUrl.split("/").pop() || "meme.png";
      link.download = filename;

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      URL.revokeObjectURL(blobUrl);
    } catch (err) {
      console.error("Download failed:", err);
      alert("Failed to download image. Try right-click -> Save as.");
    }
  };

  const shareWhatsApp = (url, text) => {
    const whatsappUrl = `https://api.whatsapp.com/send?text=${encodeURIComponent(text + " " + url)}`;
    window.open(whatsappUrl, "_blank");
  };

  const shareFacebook = (url) => {
    const fbUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
    window.open(fbUrl, "_blank");
  };

  // Helper component to render entertainment links
  const EntertainmentItem = ({ item, type }) => {
    if (!item) return null;

    let platforms = [];
    if (type === "movie") {
      platforms = [
        { name: "IMDb", icon: "🎬", url: item.imdb },
        { name: "Netflix", icon: "📺", url: item.netflix },
        { name: "YouTube", icon: "▶️", url: item.youtube },
        { name: "Search", icon: "🔍", url: item.google },
      ];
    } else if (type === "music") {
      platforms = [
        { name: "Spotify", icon: "🎵", url: item.spotify },
        { name: "YouTube", icon: "▶️", url: item.youtube },
        { name: "Apple Music", icon: "🎧", url: item.apple_music },
        { name: "Google Play", icon: "▶️", url: item.google_play },
      ];
    } else if (type === "book") {
      platforms = [
        { name: "Goodreads", icon: "📖", url: item.goodreads },
        { name: "Amazon", icon: "🛒", url: item.amazon },
        { name: "Google Books", icon: "📚", url: item.google_books },
        { name: "Kindle", icon: "📕", url: item.kindle },
      ];
    }

    return (
      <div className="entertainment-item">
        <div className="item-title">
          {type === "movie" && "🎬"}
          {type === "music" && "🎵"}
          {type === "book" && "📚"}
          {" "}
          {item.title}
          {item.artist && <span className="item-subtitle"> by {item.artist}</span>}
          {item.author && <span className="item-subtitle"> by {item.author}</span>}
        </div>
        <div className="item-links">
          {platforms.map((platform, idx) => (
            <a
              key={idx}
              href={platform.url}
              target="_blank"
              rel="noopener noreferrer"
              className="platform-link"
              title={platform.name}
            >
              <span className="platform-icon">{platform.icon}</span>
              <span className="platform-name">{platform.name}</span>
            </a>
          ))}
        </div>
      </div>
    );
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleProceed();
    }
  };

  return (
    <div className="trackmood-page">

      <AgeDisclaimerMarquee/> 


      {/* Header */}
      <header className="dashboard-header">
        <div className="logo-container" onClick={() => navigate("/")}>
          <img src={logo} alt="VibeCheck Logo" className="logo" />
          {/* <h1 className="brand-name">VibeCheck</h1> */}
          <h1 className="brand-name">
            <span className="vibe">Vibe</span>
            <span className="check">Check</span>
          </h1>
        </div>

        <nav className="nav-links">
          <button onClick={() => navigate("/")}>Home</button>
          <button onClick={() => navigate("/about")}>About</button>
          {/* <button onClick={() => navigate("/")}>Features</button> */}
          <button onClick={() => navigate("/contact")}>Contact Us</button>
        </nav>

        {user ? (
          <div className="user-dropdown-wrapper" ref={userMenuRef}>
            <button
              className="user-btn"
              onClick={() => setShowUserMenu(!showUserMenu)}
            >
              <span className="user-avatar">👤</span>
              <span className="user-name">
                {user.displayName ? user.displayName : user.email.split("@")[0]}
              </span>
              <span className={`chevron ${showUserMenu ? "open" : ""}`}>▼</span>
            </button>

            {showUserMenu && (
              <div className="user-dropdown-menu">
                {/* User Info Section */}
                <div className="user-info-section">
                  <p className="user-info-label">Logged in as</p>
                  <p className="user-display-name">
                    {user.displayName ? user.displayName : user.email.split("@")[0]}
                  </p>
                  <p className="user-email">{user.email}</p>
                </div>

                {/* Menu Items */}
                <div className="dropdown-items">
                  <button
                    className="dropdown-item"
                    onClick={() => navigate("/")}
                  >
                    <span className="item-icon">🏠</span>
                    <div className="item-content">
                      <div className="item-title">Dashboard</div>
                      <div className="item-subtitle">Go to home</div>
                    </div>
                  </button>
                </div>

                {/* Logout Button */}
                <button
                  className="dropdown-item logout-item"
                  onClick={handleLogout}
                >
                  <span className="item-icon">🚪</span>
                  <div className="item-content">
                    <div className="item-title">Logout</div>
                    <div className="item-subtitle">Sign out of account</div>
                  </div>
                </button>
              </div>
            )}
          </div>
        ) : (
          <button className="login-btn" onClick={() => navigate("/login")}>
            Login
          </button>
        )}
      </header>

      {/* Page Body - Simplified without the big background box */}
      <div className="trackmood-container">
        {/* Title Block */}
        <div className="title-block">
          <br/>
          <br/> 
          <h2>Track Mood & Generate Memes</h2>
          <p className="title-subtext">
            Share what's on your mind and let AI generate wellness tips & fun memes 🎉
          </p>
        </div>

        {/* ChatGPT-style Input Container */}
        <div className="chatgpt-input-container">
          <div className="input-wrapper">
            <textarea
              placeholder="What's on your mind?"
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={handleKeyDown}
              // disabled={isLoading}
              rows="1"
              className="chatgpt-textarea"
            />
            <button
              id="recordBtn"
              className="mic-btn-inside"
              onClick={handleVoiceRecording}
              // disabled={isLoading}
              title="Voice recording"
            >
              🎙️
            </button>
          </div>
          
          {/* Enter Button */}
          <div className="enter-button-container">
            <button
              className="proceed-btn"
              onClick={handleProceed}
              disabled={isLoading || text.trim() === ""}
            >
              {isLoading ? "Analyzing..." : "Enter"}
            </button>
          </div>
        </div>

        {/* Audio Container */}
        <div ref={audioContainerRef} id="audioContainer"></div>

        {/* Error Message */}
        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        {/* Loading Spinner */}
        {isLoading && (
          <div className="loading-container">
            <div className="spinner"></div>
          </div>
        )}

      {/* Memes Section - FIRST */}
      {memes && memes.length > 0 && (
        <div id="memesSection">
          <div className="memes-header-image">
            <img src={memesHeader} alt="Personalized Memes" />
          </div>

          <h2>Your Personalized Memes 🎉</h2>

          {/* Footer Image */}
          <div className="memes-header-image">
            <img src={memesFooter} alt="Fun Memes Footer" />
          </div>

          <div className="memes-grid">
            {memes.map((m, idx) => (
              <div key={idx} className="meme-card">
                {/* Meme Image */}
                <div className="meme-image-container">
                  <img
                    src={m.image}
                    alt={`meme-${idx}`}
                  />
                </div>

                {/* Download & Share Buttons */}
                <div className="meme-actions">
                  {/* Download Button */}
                  <button
                    className="meme-btn"
                    onClick={() => {
                      if (!user) navigate("/login");
                      else handleDownload(m.image);
                    }}
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 24 24"
                      width="30"
                      height="30"
                      fill="none"
                      stroke="white"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                      <polyline points="7 10 12 15 17 10" />
                      <line x1="12" y1="15" x2="12" y2="3" />
                    </svg>
                  </button>

                  {/* Share Button */}
                  <div className="share-dropdown-container" ref={shareMenuRef}>
                    <button
                      className="meme-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        setShareDropdownIdx(shareDropdownIdx === idx ? null : idx);
                      }}
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        width="30"
                        height="30"
                        fill="none"
                        stroke="white"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <circle cx="18" cy="5" r="3"></circle>
                        <circle cx="6" cy="12" r="3"></circle>
                        <circle cx="18" cy="19" r="3"></circle>
                        <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line>
                        <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line>
                      </svg>
                    </button>

                    {/* Dropdown */}
                    {shareDropdownIdx === idx && (
                      <div className="share-dropdown">
                        <button
                          onClick={() => {
                            if (!user) navigate("/login");
                            else shareWhatsApp(m.image, "Check out this meme!");
                          }}
                        >
                          💬 WhatsApp
                        </button>
                        <button
                          onClick={() => {
                            if (!user) navigate("/login");
                            else shareFacebook(m.image);
                          }}
                        >
                          📘 Facebook
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      </div>

      {/* Entertainment Recommendations - WITH LINKS */}
      {entertainment && (entertainment.books?.length > 0 || entertainment.music?.length > 0 || entertainment.movies?.length > 0) && (
        <div className="media-recommendations-container">
          <h2 className="media-recommendations-title">🎬 Entertainment Recommendations</h2>
          
          <div className="media-grid">
            {/* MOVIES/SERIES CARD */}
            {entertainment.movies && entertainment.movies.length > 0 && (
              <div className="media-section">
                <div className="media-section-header">🎬 Movies & Series</div>
                <div className="media-section-content">
                  {entertainment.movies.map((movie, idx) => (
                    <EntertainmentItem key={idx} item={movie} type="movie" />
                  ))}
                </div>
              </div>
            )}
            
            {/* MUSIC CARD */}
            {entertainment.music && entertainment.music.length > 0 && (
              <div className="media-section">
                <div className="media-section-header">🎵 Music</div>
                <div className="media-section-content">
                  {entertainment.music.map((song, idx) => (
                    <EntertainmentItem key={idx} item={song} type="music" />
                  ))}
                </div>
              </div>
            )}
            
            {/* BOOKS CARD */}
            {entertainment.books && entertainment.books.length > 0 && (
              <div className="media-section">
                <div className="media-section-header">📚 Books</div>
                <div className="media-section-content">
                  {entertainment.books.map((book, idx) => (
                    <EntertainmentItem key={idx} item={book} type="book" />
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* SUPPORTING LINE BELOW BOXES */}
          <div className="supporting-line-below">
            {/* 💚 Remember, taking care of yourself is the best investment you can make */}
             💛 The real person smiles in trouble, 
            gather strength from distress, and
            grows brave by reflection!  💛
          </div>
        </div>
      )}

      {/* Wellness Recommendations - THIRD */}
      {message && (
        <div id="recommendations" className="recommendations-full-container">
          <div className="rec-main-header">
            🌿 Your Wellness Recommendations
          </div>

          <div className="rec-main-body">
            <pre style={{ whiteSpace: "pre-wrap" }}>{message}</pre>
          </div>

          <div className="rec-main-footer">
            You're doing better than you think 💛
          </div>
        </div>
      )}
      
    </div>
  );
};

export default TrackAndGenerate;