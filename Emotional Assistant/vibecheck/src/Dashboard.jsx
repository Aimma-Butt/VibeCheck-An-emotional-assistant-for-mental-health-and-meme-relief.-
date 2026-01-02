import React from "react";
import homeImage from "./assets/home.png";
import { useNavigate } from "react-router-dom";
import Navbar from "./Navbar";
import AgeDisclaimerMarquee from "./AgeDisclaimerMarquee";


const Home = () => {
  const navigate = useNavigate();

  return (
    <>
      <AgeDisclaimerMarquee/> 

      {/* Top Navbar */}
      <Navbar />

      {/* Home Section */}
      <div className="section home-section">
        <div className="home-content">
          <div className="home-text">
            <h1>
              <span className="line1">Your AI-Powered</span><br />
              <span className="line2">Emotional Wellness</span><br />
              <span className="line3">Companion</span>
            </h1>

            <p>
              Take control of your emotional health with smart mood tracking, 
              personalized tips and uplifting memes to help you feel better.
            </p>

            <button
              className="get-started-btn"
              onClick={() => navigate("/trackmood")}
            >
              Get Started
            </button>
          </div>

          <div className="home-image">
            <img src={homeImage} alt="Wellness" />
          </div>
        </div>
      </div>
      {/* Footer */}
      <footer className="dashboard-footer">
        <p>© 2025 VibeCheck. All rights reserved.</p>
      </footer>
    </>
  );
};

export default Home;
