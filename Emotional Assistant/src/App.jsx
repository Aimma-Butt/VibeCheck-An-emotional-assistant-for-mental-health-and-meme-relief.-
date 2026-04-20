import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import './App.css'
import Dashboard from "./Dashboard";
import SignUp from './SignUp';
import Login from "./Login";
import Home from "./Home";
import About from "./About";
import ContactUs from "./ContactUs";
import TrackAndGenerate from './TrackAndGenerate';



function App() {
  return (
    <Router>
      <div>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<SignUp />} />
          <Route path="/trackmood" element={<TrackAndGenerate />} />
          <Route path="/home" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/contact" element={<ContactUs />} />
        </Routes>
      </div>
    </Router>
  );
}


export default App;
