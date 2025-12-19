import axios from 'axios';
import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function RecipeDetail() {
  const { id } = useParams(); // Get recipe ID from URL
  const [recipe, setRecipe] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchRecipe = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/recipe/${id}`);
        setRecipe(response.data);
      } catch (err) {
        setError('Failed to load recipe');
      }
      setLoading(false);
    };

    fetchRecipe();
  }, [id]);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;
  if (!recipe) return <p>Recipe not found</p>;

  return (
    <div className="recipe-detail">
      <h2>{recipe.title}</h2>
      <p><strong>Category:</strong> {recipe.classification}</p>
      <p><strong>Primary Ingredient:</strong> {recipe.primary_ingredient}</p>

      {recipe.recipe_source && (
        <p>
          <strong>Source:</strong>{' '}
          {recipe.is_url === "1" ? (
            recipe.recipe_source
          ) : (
            <a href={recipe.recipe_source} target="_blank" rel="noopener noreferrer">
              View URL
            </a>
          )}
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

      <Link to="/">← Back to Recipes</Link>
    </div>
  );
}

export default RecipeDetail;
