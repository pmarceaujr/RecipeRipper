import React, { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import api from "../api/axios";
// import { Link, useParams } from 'react-router-dom';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const RecipeEdit = () => {
  const { id } = useParams(); // Recipe ID from URL
  const navigate = useNavigate();

  const [recipe, setRecipe] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Fetch recipe by ID on mount
  useEffect(() => {
    const fetchRecipe = async () => {
      try {
        const res = await api.get(`${API_URL}/api/recipe/${id}`);
        setRecipe(res.data);
      } catch (err) {
        setError('Failed to load recipe');
      } finally {
        setLoading(false);
      }
    };
    fetchRecipe();
  }, [id]);

  if (loading) return <p>Loading...</p>;
  if (error) return <p className="error">{error}</p>;
  if (!recipe) return <p>Recipe not found</p>;

  // --- Handlers ---
  const handleChange = (field, value) => {
    setRecipe({ ...recipe, [field]: value });
  };

  // Ingredients
  const handleIngredientChange = (idx, field, value) => {
    const newIngredients = [...recipe.ingredients];
    newIngredients[idx][field] = value;
    setRecipe({ ...recipe, ingredients: newIngredients });
  };
  const addIngredient = () => {
    setRecipe({
      ...recipe,
      ingredients: [...recipe.ingredients, { ingredient: '', quantity: '', unit: '' }]
    });
  };
  const removeIngredient = (idx) => {
    const newIngredients = recipe.ingredients.filter((_, i) => i !== idx);
    setRecipe({ ...recipe, ingredients: newIngredients });
  };

  // Directions
  const handleDirectionChange = (idx, field, value) => {
    const newDirections = [...recipe.directions];
    newDirections[idx][field] = value;
    setRecipe({ ...recipe, directions: newDirections });
  };
  const addDirection = () => {
    setRecipe({
      ...recipe,
      directions: [...recipe.directions, { step_number: recipe.directions.length + 1, instruction: '' }]
    });
  };
  const removeDirection = (idx) => {
    const newDirections = recipe.directions.filter((_, i) => i !== idx);
    setRecipe({ ...recipe, directions: newDirections });
  };

  // Comments
  const handleCommentChange = (idx, field, value) => {
    const newComments = [...recipe.comments];
    newComments[idx][field] = value;
    setRecipe({ ...recipe, comments: newComments });
  };
  const addComment = () => {
    setRecipe({
      ...recipe,
      comments: [...recipe.comments, { comments: '' }]
    });
  };
  const removeComment = (idx) => {
    const newComments = recipe.comments.filter((_, i) => i !== idx);
    setRecipe({ ...recipe, comments: newComments });
  };  


  // Submit
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await api.put(`${API_URL}/api/recipe/${id}`, recipe);
      alert('Recipe updated!');
      navigate(`/recipe/${id}`);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update recipe');
    }
  };

const formattedDate = new Date(recipe.created_at).toLocaleString("en-US", { 
    year: "numeric", 
    month: "long", 
    day: "numeric", 
    hour: "2-digit", 
    minute: "2-digit", 
    hour12: true });

  return (
    <div className="recipe-detail">
      <h2>Edit Recipe: {recipe.title}</h2>
      {error && <p className="error">{error}</p>}
      <form onSubmit={handleSubmit}>
        <div className="edit-container">
          {/* LEFT SIDE */}
          <div className="edit-left">
              <div>
              <label className='recipe-edit-label'>Recipe Name:</label>
                <input
                  className='recipe-edit-input-text'
                  type="text"
                  value={recipe.title}
                  onChange={(e) => handleChange('title', e.target.value)}
                  required
                />
            </div>
            <div>
              <label className='recipe-edit-label'>Course:</label>
              <input
                className='recipe-edit-input-text'
                type="text"
                value={recipe.course}
                onChange={(e) => handleChange('course', e.target.value)}
              />
            </div>
            <div>
              <label className='recipe-edit-label'>Cuisine:</label>
              <input
                className='recipe-edit-input-text'
                type="text"
                value={recipe.cuisine}
                onChange={(e) => handleChange('cuisine', e.target.value)}
              />
            </div>
            <div>
              <label className='recipe-edit-label'>Primary Ingredient:</label>
              <input
                className='recipe-edit-input-text'
                type="text"
                value={recipe.primary_ingredient}
                onChange={(e) => handleChange('primary_ingredient', e.target.value)}
              />
            </div>
            <div>
              <label className='recipe-edit-label'>Source URL (Read Only):</label>
              <input
                className='recipe-edit-input-text'
                type="text"
                value={recipe.recipe_source}
                readOnly
              />
            </div>        
          </div>
          {/* RIGHT SIDE */}
          <div className="edit-right">
              <div>
              <label className='recipe-edit-label'>Prep Time (minutes):</label>
                <input
                  className='recipe-edit-input-text'
                  type="text"
                  value={recipe.prep_time}
                  onChange={(e) => handleChange('prep_time', e.target.value)}
                  required
                />
            </div>
            <div>
              <label className='recipe-edit-label'>Cook Time (minutes):</label>
              <input
                className='recipe-edit-input-text'
                type="text"
                value={recipe.cook_time}
                onChange={(e) => handleChange('cook_time', e.target.value)}
              />
            </div>
            <div>
              <label className='recipe-edit-label'>Total Time (minutes):</label>
              <input
                className='recipe-edit-input-text'
                type="text"
                value={recipe.total_time}
                onChange={(e) => handleChange('total_time', e.target.value)}
              />
            </div>
            <div>
              <label className='recipe-edit-label'>Servings:</label>
              <input
                className='recipe-edit-input-text'
                type="text"
                value={recipe.servings}
                onChange={(e) => handleChange('servings', e.target.value)}
              />
            </div>
            <div>
              <label className='recipe-edit-label'>Imported On (Read Only):</label>
              <input
                className='recipe-edit-input-text'
                type="text"
                value={formattedDate}
                readOnly
              />
            </div> 
          </div>
        </div>
        <p>
          <hr />
        </p>
        {/* Ingredients */}
        <h3>Ingredients</h3>

        <table class="ingredient-table">
          <thead>
            <tr>
              <th className='ingredient-item-th-td'>Item</th>
              <th className='ingredient-qty-th-td'>Qty</th>
              <th className='ingredient-unit-th-td'>Measure</th>
              <th className='ingredient-delete-th-td'>Delete</th>
            </tr>
          </thead>
          <tbody>
            {recipe.ingredients.map((ing, idx) => (
              <tr key={idx}>
                <td className='ingredient-item-th-td'>
                  <input
                    className="ingredients-input-item"
                    type="text"
                    value={ing.ingredient}
                    placeholder="Ingredient"
                    onChange={(e) => handleIngredientChange(idx, 'ingredient', e.target.value)}
                  />
                </td>
                <td className='ingredient-qty-th-td'>
                  <input
                    className="ingredients-input-qty"
                    type="text"
                    value={ing.quantity}
                    placeholder="Quantity"
                    onChange={(e) => handleIngredientChange(idx, 'quantity', e.target.value)}
                  />
                </td>
                <td className='ingredient-unit-th-td'>
                  <input
                    className="ingredients-input-unit"
                    type="text"
                    value={ing.unit}
                    placeholder="Unit"
                    onChange={(e) => handleIngredientChange(idx, 'unit', e.target.value)}
                  />
                </td>
                <td className='ingredient-delete-th-td'>
                  <button
                    className="edit-btn"
                    type="button"
                    onClick={() => removeIngredient(idx)}
                  >
                    ❌
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <button className="add-button" type="button" onClick={addIngredient}>
          ➕ Add Ingredient
        </button>
        <p>
          <hr />
        </p>
        {/* Directions */}
        <h3>Directions</h3>

        <table class="directions-table">
          <thead>
            <tr>
              <th className='direction-step-th-td'>Step</th>
              <th className='direction-instruction-th-td'>Instruction</th>
              <th className='direction-delete-th-td'>Delete</th>
            </tr>
          </thead>
          <tbody>
            {recipe.directions.map((dir, idx) => (
              <tr key={idx}>

                <td className='direction-step-th-td'>
                  <input
                    className="directions-input-step"
                    type="number"
                    value={dir.step_number}
                    onChange={(e) => handleDirectionChange(idx, 'step_number', e.target.value)}
                  />
                </td>

                <td className='direction-instruction-th-td'>
                  <input
                    className='directions-input-text'
                    type="text"
                    value={dir.instruction}
                    placeholder="Instruction"
                    onChange={(e) => handleDirectionChange(idx, 'instruction', e.target.value)}
                  />
                </td>

                <td className='direction-delete-th-td'>
                  <button className="edit-btn" type="button" onClick={() => removeDirection(idx)}>❌</button>
                </td>




              </tr>
            ))}
            <button className="add-button" type="button" onClick={addDirection}>➕ Add Step</button>
          </tbody>
        </table>
        <p>
          <hr />
        </p>

        {/* Comments */}
        <h3>Comments</h3>
        <table class="comments-table">
          <thead>
            <tr>
              <th className='comment-th-td'>Comments</th>
              <th className='comment-delete-th-td'>Delete</th>
            </tr>
          </thead>
          <tbody>
            {recipe.comments.map((comment, idx) => (
              <tr key={idx} className="comment-row">
                <td className='comment-th-td'>
                  {/* <input
                  type="number"
                  value={comment.id}
                  onChange={(e) => handleCommentChange(idx, 'id', e.target.value)}
                /> */}
                  <input
                    className='comments-input-text'
                    type="text"
                    value={comment.comments}
                    placeholder="Comments"
                    onChange={(e) => handleCommentChange(idx, 'comments', e.target.value)}
                  />
                </td>
                <td className='comment-delete-th-td'>
                  <button className="edit-btn" type="button" onClick={() => removeComment(idx)}>❌</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <button className="add-button" type="button" onClick={addComment}>➕ Add Comment</button>
        <p>
          <hr />
        </p>
        <div>
          <button className="save-button" type="submit">Save Recipe</button>
        </div>
      </form>
      <p>
        <hr />
      </p>      
      <Link to="/recipes">← Back to Recipes</Link>
    </div>
  );
};

export default RecipeEdit;
