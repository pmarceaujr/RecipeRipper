import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import "../css/LandingPage.css";

export default function LandingPage() {
  return (
    <div className="landing-container">
      <div className="landing-content">
        <h1>Welcome to The Recipe Ripper Database!</h1>
        <p>Your personal place on the web to store, search, and organize your favorite recipes.</p>

        {/* Link to your React login page */}
        <a href="/login" className="login-link">
          Go to Login
        </a>

        {/* Video placeholder */}
        <div >
          Should be playing a video here
          <video width="400" autoPlay loop muted playsInline>
            <source src="/videos/Recipe_Webpage_Scrolling.mp4" type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        </div>
      </div>
    </div>
  );
}
