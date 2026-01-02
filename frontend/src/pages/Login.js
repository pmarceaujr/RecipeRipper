import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import Logo from "./ImportLogo";

const API_URL = process.env.REACT_APP_API_URL 

export default function Login() {
  const [userId, setUserId] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState(null);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleRegister = () => {
    navigate("/register");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage(null); // Clear previous messages

    try {
      const res = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ userId, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setMessage(data.error || "Login failed");
        return;
      }

      login(data.access_token);
      navigate("/recipes");
    } catch (err) {
      setMessage("Login error. Please check your credentials and try again.");
      console.error(err);
    }
  };

  return (
    <div>
      <div className="container-login">
        <Logo alt="Recipe Ripper Logo" width="500" />
        <form className="login-form" onSubmit={handleSubmit}>
          <div>
          </div>
          <h2>Login</h2>
          <p>If you have an account, enter your email/username and password to log in.</p>
          <p>If you do not have an account, click the Register button below to create an account.</p>

          {message && (
            <p style={{
              color: message.includes("success") ? "green" : "red",
              backgroundColor: "#f0f0f0",
              fontWeight: "bold",
              margin: "1rem 0"
            }}>
              {message}
            </p>
          )}

          <div>
            <label className='login-label'>Email or Username:</label>
            <input
              className='login-input-text'
              type="text"
              placeholder="Email or Username"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
            />
          </div>
          <div>
            <label className='login-label'>Password:</label>
            <input
              className='login-input-text'
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <div className="login-div">
            <button align="right" type="submit">Login</button>
            <button align="left" onClick={handleRegister}>Register</button>
          </div>
        </form>
      </div>
    </div >
  );
}
