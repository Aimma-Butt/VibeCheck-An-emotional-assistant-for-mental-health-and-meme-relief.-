import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css";
import loginImg from "./assets/login.png";

// Firebase imports
import { signInWithEmailAndPassword, GoogleAuthProvider, signInWithPopup } from "firebase/auth";
import { auth } from "./firebase";

function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  // -----------------------
  // EMAIL + PASSWORD LOGIN
  // -----------------------
  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      await signInWithEmailAndPassword(auth, email, password);
      // alert("Logged in successfully!");
      navigate("/trackmood");   // redirect to your dashboard page
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="login-container">
      {/* Back button */}
      <button className="back-btn" onClick={() => navigate("/")}>
        ← Home
      </button>

      {/* Left image */}
      <div className="login-left">
        <img src={loginImg} alt="login illustration" />
      </div>

      {/* Right form */}
      <div className="login-right">
        <center><h2>Log in</h2></center>
        <center>
          <p className="login-subtext">
            Log in with your data that you entered during your registration
          </p>
        </center>

        {/* Error message */}
        {error && <p className="error-msg">{error}</p>}

        <form onSubmit={handleLogin}>
          <label>Enter your email address</label>
          <input 
            type="email" 
            placeholder="name@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <label>Enter your password</label>
          <input 
            type="password" 
            placeholder="atleast 8 characters"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <a href="#" className="forget-password">Forget password?</a>

          <button type="submit">Log in</button>
        </form>

        <p className="register-text">
          Don’t have an account? <a href="/signup">Sign Up</a>
        </p>
      </div>
    </div>
  );
}

export default Login;
