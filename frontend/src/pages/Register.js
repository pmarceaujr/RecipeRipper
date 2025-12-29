import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Logo from "./ImportLogo";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [username, setUsername] = useState("");  
  const [firstname, setFirstname] = useState(""); 
  const [lastname, setLastname] = useState(""); 
  const [message, setMessage] = useState(null);
  const [confirmPassword, setConfirmPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      setMessage("Passwords do not match.");
      return;
    }
    setMessage(null); // Clear previous messages
    try {
      const res = await fetch(`${API_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, username, password, firstname, lastname }),
      });

      const data = await res.json(); // ← very important!

      if (res.ok) {
        setMessage("Account created! Redirecting to login...");
        setTimeout(() => navigate("/login"), 1500);
      } else {
        // Handle specific backend error messages
        setMessage(data.error || "Registration failed. Please try again.");
      }
    } catch (err) {
      setMessage("Network error. Please check your connection.");
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
          <h2>Register</h2>
          <p>To create an account, please complete the form below. You can only login if you have an account.</p>

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
            <label className='login-label'>Email:</label>
            <input
              className='login-input-text'
              type="text"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div>
            <label className='login-label'>Username:</label>
            <input
              className='login-input-text'
              type="text"          
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>
          <div>
            <label className='login-label'>First Name:</label>
            <input
              className='login-input-text'
              type="text"          
              placeholder="First Name"
              value={firstname}
              onChange={(e) => setFirstname(e.target.value)}
            />
          </div>
          <div>
            <label className='login-label'>Last Name:</label>
            <input
              className='login-input-text'
              type="text"          
              placeholder="Last Name"
              value={lastname}
              onChange={(e) => setLastname(e.target.value)}
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
          <div>
            <label className='login-label'>Confirm Password:</label>
            <input
              className='login-input-text'
              type="password"
              placeholder="Confirm Password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
            />
          </div>
          <div className="login-div">
            <button type="submit">Register</button>
          </div>
        </form>
      </div> {/* End container */}
    </div>
  );
}
