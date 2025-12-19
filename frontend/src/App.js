import axios from 'axios';
import React, { useEffect, useState } from 'react';
import './App.css';

// Use environment variable or default to localhost
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function App() {
  const [recipes, setRecipes] = useState([]);
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);

  useEffect(() => {
    fetchRecipes();
  }, []);

  const fetchRecipes = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/recipes`);
      setRecipes(response.data);
    } catch (err) {
      console.error('Error fetching recipes:', err);
      setError('Failed to load recipes');
    }
  };

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
    setError('');
  };

  const handleFileUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError('');
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post(`${API_URL}/api/recipes/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      alert(`Success! Added: ${response.data.title}`);
      setSelectedFile(null);
      document.getElementById('fileInput').value = '';
      await fetchRecipes();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to upload recipe');
    }
    setLoading(false);
  };

  const handleUrlSubmit = async (e) => {
    e.preventDefault();
    if (!url) return;

    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API_URL}/api/recipes/from-url`, { url });
      alert(`Success! Added: ${response.data.title}`);
      setUrl('');
      await fetchRecipes();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to add recipe from URL');
    }
    setLoading(false);
  };

  const handleDelete = async (id, title) => {
    if (!window.confirm(`Delete "${title}"?`)) return;

    try {
      await axios.delete(`${API_URL}/api/recipes/${id}`);
      await fetchRecipes();
    } catch (err) {
      setError('Failed to delete recipe');
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🍳 Recipe Database</h1>
      </header>

      <div className="container">
        {/* Add Recipe Section */}
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
                  {loading ? 'Processing...' : 'Upload & Parse'}
                </button>
              </div>
            )}
          </div>

          {/* URL Input */}
          <div className="upload-option">
            <h3>🔗 Add from URL</h3>
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
                {loading ? 'Processing...' : 'Add Recipe'}
              </button>
            </form>
          </div>
        </div>

        {/* Recipe List */}
        <div className="recipes-section">
          <h2>My Recipes ({recipes.length})</h2>

          {loading && <p className="loading">Loading...</p>}

          <div className="recipes-grid">
            {recipes.map(recipe => (
              <div key={recipe.id} className="recipe-card">
                <div className="recipe-header">
                  <h3>{recipe.title}</h3>
                  <button
                    className="delete-btn"
                    onClick={() => handleDelete(recipe.id, recipe.title)}
                  >
                    🗑️
                  </button>
                </div>

                <p className="recipe-category">
                  <strong>Category:</strong> {recipe.classification}
                </p>

                {recipe.source_url && (
                  <p className="recipe-source">
                    <strong>Source:</strong>{' '}
                    <a href={recipe.source_url} target="_blank" rel="noopener noreferrer">
                      View Original
                    </a>
                  </p>
                )}

                <div className="recipe-section">
                  <h4>Ingredients</h4>
                  <ul>
                    {recipe.ingredients.map((ing, idx) => (
                      <li key={idx}>
                        {ing.quantity && `${ing.quantity} `}
                        {ing.unit && `${ing.unit} `}
                        {ing.ingredient}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="recipe-section">
                  <h4>Directions</h4>
                  <ol>
                    {recipe.directions.map(dir => (
                      <li key={dir.step_number}>{dir.instruction}</li>
                    ))}
                  </ol>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;