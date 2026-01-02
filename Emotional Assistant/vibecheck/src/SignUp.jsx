import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createUserWithEmailAndPassword } from "firebase/auth";
import { auth } from "./firebase";
import "./SignUp.css";
import signupImg from "./assets/signup.png";

function SignUp() {
  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      await createUserWithEmailAndPassword(auth, email, password);

      alert("Account created successfully!");
      navigate("/login");
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="signup-container">
      <button className="back-btn" onClick={() => navigate("/")}>← Home</button>

      <div className="signup-left">
        <img src={signupImg} alt="signup illustration" />
      </div>

      <div className="signup-right">
        <center><h2>SIGN UP</h2></center>
        <center>
          <p>
            Already have an account? <a href="/login">Log in</a>
          </p>
        </center>

        {error && <p className="error-msg">{error}</p>}

        <form onSubmit={handleSubmit}>
          <label>Full Name</label>
          <input type="text" placeholder="Abc Xyz"
            value={fullName} onChange={(e) => setFullName(e.target.value)}
          />

          <label>Email</label>
          <input type="email" placeholder="abczy45@gmail.com"
            value={email} onChange={(e) => setEmail(e.target.value)}
          />

          <label>Password</label>
          <input type="password" placeholder="••••••••"
            value={password} onChange={(e) => setPassword(e.target.value)}
          />

          <button type="submit">Sign Up</button>
        </form>
      </div>
    </div>
  );
}

export default SignUp;
