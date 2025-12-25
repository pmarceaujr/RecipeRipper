import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    const res = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const data = await res.json();

    if (!res.ok) {
      setError(data.error || "Login failed");
      return;
    }

    login(data.access_token);
    navigate("/recipes");
  };

  return (
    <div>
      <div className="container-login">
        <form onSubmit={handleSubmit}>
          <h2>Login</h2>

          {error && <p style={{ color: "red" }}>{error}</p>}
          <div>
            <label className='recipe-edit-label'>Email or Username:</label>
            <input
              placeholder="Email or Username"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div>
            <label className='recipe-edit-label'>Password:</label>
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <button align="right" type="submit">Login</button>
        </form>

      </div>

      <label className='recipe-edit-label'>Don't have an account? You can register here: </label> <a href="/register">Register</a>
    </div >
  );
}
