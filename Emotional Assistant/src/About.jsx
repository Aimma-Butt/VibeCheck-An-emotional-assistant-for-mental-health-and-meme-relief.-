import React from "react";
import Navbar from "./Navbar";

const About = () => {
  return (
    <>
      {/* Top Navbar */}
      <Navbar />

      {/* About Section */}
      <div className="section about-section">
        <h2>
          What is <span className="highlight">VibeCheck?</span>
        </h2>
        <p>
          VibeCheck is your personal emotional wellness assistant that makes 
          mental health tracking simple and uplifting. Every time you share 
          how you're feeling, our system analyzes your mood, offers supportive
          insights. You can also generate personalized memes to add some 
          laughter to your day. Because healing doesn't always have to be 
          serious—it can be fun too.
        </p>
      </div>
      {/* Footer */}
      <footer className="dashboard-footer">
        <p>© 2025 VibeCheck. All rights reserved.</p>
      </footer>
    </>
  );
};

export default About;
