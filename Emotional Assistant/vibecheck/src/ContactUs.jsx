import React from "react";
import Navbar from "./Navbar";

const ContactUs = () => {
  return (
    <>
      {/* Top Navbar */}
      <Navbar />

      {/* Contact Section */}
      <div className="section contact-section">
        <div className="contact-wrapper">

          {/* Left Side */}
          <div className="contact-left">
            <h2>Get in Touch</h2>

            <p className="subtitle">I’d like to hear from you!</p>

            <p className="description">
              If you have any inquiries or just want to say hi, please use the contact form!
            </p>

            <div className="contact-email">
              <a href="mailto:support@vibecheck.com">support@vibecheck.com</a>
            </div>

            <div className="social-icons">
              <i className="fa fa-facebook"></i>
              <i className="fa fa-instagram"></i>
              <i className="fa fa-twitter"></i>
              <i className="fa fa-linkedin"></i>
            </div>
          </div>

          {/* Right Side - Form */}
          <div className="contact-form">
            <div className="form-row">
              <input placeholder="First Name" type="text" />
              <input placeholder="Last Name" type="text" />
            </div>

            <input placeholder="Email *" type="email" className="full-input" />

            <textarea placeholder="Message" rows="5"></textarea>

            <button className="send-btn">Send</button>
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

export default ContactUs;
