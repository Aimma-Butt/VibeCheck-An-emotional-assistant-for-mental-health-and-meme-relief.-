import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "./Dashboard.css"; // reuse your existing styles
import logo from "./assets/VC.png";
// import "./Navbar.css"

const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // Check which page is active
  const isActive = (path) => (location.pathname === path ? "active" : "");

  return (
    <header className="dashboard-header">
      
      <div className="logo-container" onClick={() => navigate("/")}>
        <img src={logo} alt="VibeCheck Logo" className="logo" />

        <h1 className="brand-name">
          <span className="vibe">Vibe</span>
          <span className="check">Check</span>
        </h1>
      </div>

      <nav className="nav-links">
        <button className={isActive("/home")} onClick={() => navigate("/")}>Home</button>
        <button className={isActive("/about")} onClick={() => navigate("/about")}>About</button>
        <button className={isActive("/contact")} onClick={() => navigate("/contact")}>Contact Us</button>
      </nav>

      <button className="login-btn" onClick={() => navigate("/login")}>Login</button>
    </header>
  );
};

export default Navbar;
