import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import api from "../api/axios";

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function RecipeDetail() {
  const { id } = useParams(); // Get recipe ID from URL
  const [recipe, setRecipe] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchRecipe = async () => {
      try {
        const response = await api.get(`${API_URL}/api/recipe/${id}`);
        setRecipe(response.data);
      } catch (err) {
        setError('Failed to load recipe');
      }
      setLoading(false);
    };

    fetchRecipe();
  }, [id]);

  // Simple print handler
  const handlePrint = () => {
    window.print();
  };  

  if (loading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;
  if (!recipe) return <p>Recipe not found</p>;

const formattedDate = new Date(recipe.created_at).toLocaleString("en-US", { 
    year: "numeric", 
    month: "long", 
    day: "numeric", 
    hour: "2-digit", 
    minute: "2-digit", 
    hour12: true });


  return (
    <div className="recipe-detail">
      {/* Header with title and print button */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '1.5rem',
        flexWrap: 'wrap',
        gap: '1rem'
      }}>
        <h2 style={{ margin: 0 }}>{recipe.title}</h2>

        {/* Print Button */}
        <button
          onClick={handlePrint}
          title="Print this recipe"
          style={{
            padding: '8px 16px',
            backgroundColor: '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '1rem',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            transition: 'background-color 0.2s'
          }}
          onMouseOver={e => e.currentTarget.style.backgroundColor = '#45a049'}
          onMouseOut={e => e.currentTarget.style.backgroundColor = '#4CAF50'}
        >
          🖨️ Print
        </button>
      </div>


      <p className='detail-p'>
        <strong>Course:</strong> {recipe.course}
        <span style={{ marginLeft: "25px" }}></span>
        <strong>Primary Ingredient:</strong> {recipe.primary_ingredient}
        <span style={{ marginLeft: "25px" }}></span>
        <strong>Cuisine:</strong> {recipe.cuisine}
      </p>

      <p className='detail-p'>
        <strong>Prep Time:</strong> {recipe.prep_time} minutes
        <span style={{ marginLeft: "25px" }}></span>
        <strong>Cook Time:</strong> {recipe.cook_time} minutes
        <span style={{ marginLeft: "25px" }}></span>
        <strong>Total Time:</strong> {recipe.total_time} minutes
        <span style={{ marginLeft: "25px" }}></span>
        <strong>Servings:</strong> {recipe.servings}
        <span style={{ marginLeft: "25px" }}></span>
      </p>      

      {recipe.recipe_source && (
        <p className='detail-p'>
          <strong>Source:</strong>{' '}
          {recipe.is_url === "1" ? (
            recipe.recipe_source
          ) : (
            <a href={recipe.recipe_source} target="_blank" rel="noopener noreferrer">
              View URL
            </a>
          )}
          <span style={{ marginLeft: "25px" }}></span>
          <strong>Imported On:</strong> {formattedDate}
        </p>
      )}

      <div>
        <h3>Ingredients</h3>
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

      <div>
        <h3>Directions</h3>
        <ol>
          {recipe.directions.map(dir => (
            <li key={dir.step_number}>{dir.instruction}</li>
          ))}
        </ol>
      </div>

      <div>
        <h3>Comments</h3>
        <ol>
          {recipe.comments.map(comment => (
            <li key={comment.id}>{comment.comments}</li>
          ))}
        </ol>
      </div>
      <p>
        <hr />
      </p>
      <Link to="/recipes">← Back to Recipes</Link>
    </div>
  );
}

export default RecipeDetail;
