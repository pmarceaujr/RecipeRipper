import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/axios";
import { useAuth } from "../auth/AuthContext";

import "../App.css";

// Use environment variable or default to localhost
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

export default function RecipeList() {
  const [recipes, setRecipes] = useState([]);
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const { logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchRecipes();
  }, []);

const handleLogout = () => {
  logout();
  navigate("/login");
};

  const fetchRecipes = async () => {
    try {
      const response = await api.get("/api/recipes");
      console.log("Fetched recipes:", response.config.headers);
      setRecipes(response.data);
    } catch (err) {
      console.error("Error fetching recipes:", err);
      setError("Failed to load recipes");
    }
  };

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
    setError("");
  };

  const handleFileUpload = async () => {
    if (!selectedFile) {
      setError("Please select a file first");
      return;
    }

    setLoading(true);
    setError("");
    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await api.post(
        "/api/recipes/upload",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      alert(`Success! Added: ${response.data.title}`);
      setSelectedFile(null);
      document.getElementById("fileInput").value = "";
      await fetchRecipes();
    } catch (err) {
      setError(err.response?.data?.error || "Failed to upload recipe");
    }

    setLoading(false);
  };

  const handleUrlSubmit = async (e) => {
    e.preventDefault();
    if (!url) return;

    setLoading(true);
    setError("");

    try {
      const response = await api.post(
        "/api/recipes/from-url",
        { url }
      );

      alert(`Success! Added: ${response.data.title}`);
      setUrl("");
      await fetchRecipes();
    } catch (err) {
      setError(err.response?.data?.error || "Failed to add recipe from URL");
    }

    setLoading(false);
  };

  const handleDelete = async (id, title) => {
    if (!window.confirm(`Delete "${title}"?`)) return;

    try {
      await api.delete(`${API_URL}/api/recipe/${id}`);
      await fetchRecipes();
    } catch (err) {
      setError("Failed to delete recipe");
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🍳 The Recipe Ripper Database</h1>
        <button
            onClick={handleLogout}
            style={{
              position: "absolute",
              top: "20px",
              right: "20px",
              padding: "8px 12px",
              cursor: "pointer",
            }}>
            Logout
        </button>        
      </header>

      <div className="container">
        {/* LEFT SIDE */}
        <div className="left">
          <div className="add-recipe-section">
            <h2>Add New Recipe</h2>

            {error && <div className="error-message">{error}</div>}

            {/* File Upload */}
            <div className="upload-option">
              <h3>📁 Upload File</h3>
              <p className="file-info">Supports: TXT, PDF, JPG, PNG</p>

              <input
                id="fileInput"
                type="file"
                onChange={handleFileChange}
                accept=".txt,.pdf,.jpg,.jpeg,.png"
                disabled={loading}
              />

              {selectedFile && (
                <div>
                  <p>Selected: {selectedFile.name}</p>
                  <button onClick={handleFileUpload} disabled={loading}>
                    {loading ? "Processing..." : "Upload & Parse"}
                  </button>
                </div>
              )}
            </div>

            {/* URL Input */}
            <div className="upload-option">
              <h3>🔗 Add from URL</h3>
              <p>By importing a recipe, you confirm this content is for your personal use only.</p>

              <form onSubmit={handleUrlSubmit}>
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://example.com/recipe"
                  disabled={loading}
                  required
                />

                <button type="submit" disabled={loading}>
                  {loading ? "Processing..." : "Add Recipe"}
                </button>
              </form>
            </div>
          </div>
        </div>

        {/* RIGHT SIDE */}
        <div className="right">
          <div className="recipe-section">
            <h2>My Recipes ({recipes.length})</h2>

            {loading && <p className="loading">Loading...</p>}

            <div className="recipes-grid">
              {recipes.map((recipe) => (
                <div key={recipe.id} className="recipe-card">
                  <div className="recipe-header">
                    <h3>
                      <Link to={`/recipe/${recipe.id}`}>
                        {recipe.title}
                      </Link>
                    </h3>


                  </div>

                  <p className="recipe-category">
                    <strong>Course:</strong>{" "}
                    {recipe.course} {" "}
                    <span style={{ marginLeft: "10px" }}></span>
                    <strong>Cuisine:</strong>{" "}
                    {recipe.cuisine}
                    <span style={{ marginLeft: "10px" }}></span>
                    <strong>Main Ingredient:</strong>{" "}
                    {recipe.primary_ingredient} {""}
                    <span style={{ marginLeft: "10px" }}></span>
                    <strong>Total Time:</strong>{" "}
                    {recipe.total_time}                    
                  </p>

                  {recipe.recipe_source && (
                    <p className="recipe-source">
                      <strong>Source:</strong>{" "}
                      {recipe.is_url === "1" ? (
                        recipe.recipe_source
                      ) : (
                        <a
                          href={recipe.recipe_source}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          View URL
                        </a>
                      )}
                    </p>
                  )}
                    <div className="recipe-actions">
                      <div className="tooltip">
                        <Link to={`/recipe/${recipe.id}/edit`} className="edit-btn" title="Edit">✏️</Link>

                      </div>
                      <div className="tooltip">
                      <button className="delete-btn" onClick={() => handleDelete(recipe.id, recipe.title)} title="Delete">🗑️</button>

                      </div>

                    </div>                  
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}