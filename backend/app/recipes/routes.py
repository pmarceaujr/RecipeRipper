# app/routes/recipes.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from ..extensions import db
from ..models.recipe import Recipe
from ..models.ingredient import Ingredient
from ..models.direction import Direction
from ..models.comment import Comment
from ..utils.database import get_all_recipes, get_recipe_by_id, update_recipe_by_id, delete_recipe, save_recipe   
from ..utils.parser import *

recipes_bp = Blueprint('recipes', __name__)

ALLOWED_EXTENSIONS = {'.txt', '.pdf', '.jpg', '.jpeg', '.png'}

def allowed_file(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

@recipes_bp.route('/recipes', methods=['GET'])
@jwt_required()
def get_recipes():
    print("Fetching all recipes")
    """Get all recipes"""
    try:
        
        user_id = get_jwt_identity()
        print(f"User ID: {user_id}")
        recipes = get_all_recipes(user_id)
        if not recipes or len(recipes) == 0:
            return jsonify({"msg": "You currently do not have any recipes saved."}), 204         
        return jsonify(recipes)
    except Exception as e:
        current_app.logger.error(f"Error fetching recipes: {e}")
        return jsonify({"error": "Failed to fetch recipes"}), 500

@recipes_bp.route('/recipe/<int:recipe_id>', methods=['GET'])
@jwt_required()
def get_recipe(recipe_id):
    print(f"Fetching recipe with ID: {recipe_id}")
    """Get a single recipe by ID"""
    try:
        user_id = get_jwt_identity()
        print(f"User ID: {user_id}")
        recipe = get_recipe_by_id(recipe_id, user_id)
        if not recipe:
            return jsonify({"error": "Recipe not found"}), 404
        return jsonify(recipe)
    except Exception as e:
        current_app.logger.error(f"Error fetching recipe {recipe_id}: {e}")
        return jsonify({"error": "Failed to fetch recipe"}), 500

@recipes_bp.route('/recipe/<int:recipe_id>', methods=['PUT'])
@jwt_required()
def update_recipe(recipe_id):
    print("Updating recipe")
    """Update a recipe"""
    try:
        user_id = get_jwt_identity()
        print(f"User ID: {user_id}")        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        updated_recipe = update_recipe_by_id(recipe_id, user_id, data)
        if not updated_recipe:
            return jsonify({"error": "Recipe not found"}), 404
        return jsonify(updated_recipe)
    except Exception as e:
        current_app.logger.error(f"Error updating recipe {recipe_id}: {e}")
        return jsonify({"error": "Failed to update recipe"}), 500

@recipes_bp.route('/recipe/<int:recipe_id>', methods=['DELETE'])
@jwt_required()
def delete_recipe(recipe_id):
    """Delete a recipe"""
    print("Deleting recipe")
    try:
        user_id = get_jwt_identity()
        print(f"User ID: {user_id}")
        recipe = Recipe.query.filter_by(id=recipe_id, user_id=user_id).first()
        if not recipe:
            return jsonify({"error": "Recipe not found"}), 404
        db.session.delete(recipe)
        db.session.commit()
        return jsonify({"message": "Recipe deleted successfully"})
    except Exception as e:
        current_app.logger.error(f"Error deleting recipe {recipe_id}: {e}")
        return jsonify({"error": "Failed to delete recipe"}), 500

@recipes_bp.route('/recipes/upload', methods=['POST'])
@jwt_required()
def upload_recipe():
    """Upload and parse a recipe file"""
    try:
        user_id = get_jwt_identity()
        print(f"User ID: {user_id}")
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        if not allowed_file(file.filename):
            return jsonify({
                "error": f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            }), 400

        # Save file
        filename = file.filename
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        try:
            # Extract text based on type
            ext = os.path.splitext(filename)[1].lower()
            if ext in {'.jpg', '.jpeg', '.png'}:
                text = extract_text_from_image(file_path)
            elif ext == '.pdf':
                text = extract_text_from_pdf(file_path, filename)
            else:  # .txt
                text = parse_from_file(file_path, filename)

            # Parse into structured recipe
            recipe_data = parse_recipe_text(
                text, recipe_source=filename, is_file=True
            )

            # Save to DB
            recipe_id = save_recipe(recipe_data, user_id=user_id)

            return jsonify({
                "message": "Recipe added successfully",
                "recipe_id": recipe_id,
                "title": recipe_data.get('title', 'Untitled')
            })

        finally:
            # Always clean up uploaded file
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as cleanup_error:
                current_app.logger.warning(f"Failed to delete temp file {file_path}: {cleanup_error}")

    except Exception as e:
        current_app.logger.error(f"Upload failed: {e}")
        return jsonify({"error": "Failed to process upload"}), 500

@recipes_bp.route('/recipes/from-url', methods=['POST'])
@jwt_required()
def add_from_url():
    print("Adding recipe from URL")
    """Add recipe by scraping a URL"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        url = data.get('url')

        if not url:
            return jsonify({"error": "No URL provided"}), 400

        scraped_text = scrape_url(url)
        if not scraped_text.strip():
            return jsonify({"error": "Could not extract text from URL"}), 400

        recipe_data = parse_recipe_text(
            scraped_text, recipe_source=url, is_file=False
        )
        print("Parsed recipe data:")
        recipe_id = save_recipe(recipe_data, user_id=user_id)

        return jsonify({
            "message": "Recipe added successfully from URL",
            "recipe_id": recipe_id,
            "title": recipe_data.get('title', 'Untitled')
        })

    except Exception as e:
        current_app.logger.error(f"URL import failed: {e}")
        return jsonify({"error": "Failed to import from URL"}), 500