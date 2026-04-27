# app/routes/recipes.py
import threading

from requests import HTTPError

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import uuid
from ..extensions import db
from ..jobs import create_job, set_result, set_error, get_job
from ..models.recipe import Recipe
from ..models.ingredient import Ingredient
from ..models.direction import Direction
from ..models.comment import Comment
from ..utils.database import get_all_recipes, get_recipe_by_id, update_recipe_by_id, delete_recipe, save_recipe, get_picklist_values  
from ..utils.parser import *
import logging

# Configure logging
logging.basicConfig(
# filename="C:\\Users\\marceaup\\OneDrive - Illumination Works, llc\\Documents\\Projects\\zCalendarSync\\CalendarSync\\logs\\J1OutlookToGoogleSync.log",
level=logging.INFO,
format="%(asctime)s - %(levelname)s - %(funcName)s - %(lineno)d - %(message)s"
)

recipes_bp = Blueprint('recipes', __name__)

ALLOWED_EXTENSIONS = {'.txt', '.pdf', '.jpg', '.jpeg', '.png'}

def allowed_file(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS


@recipes_bp.route("/recipe-values", methods=["GET"])
@jwt_required()
def get_recipe_values():
    logging.info("Populating Picklist values")
    user_id = get_jwt_identity()
    value_type = request.args.get("type")

    if value_type not in ["course", "cuisine", "primary_ingredient"]:
        return jsonify({"error": "Invalid type"}), 400

    try:
        # Query distinct values from the Recipe table
        values = get_picklist_values(user_id, value_type)
        return jsonify(values), 200

    except Exception as e:
        logging.error(f"Error fetching recipe values: {e}")
        return jsonify({"error": "Server error"}), 500


@recipes_bp.route('/recipes', methods=['GET'])
@jwt_required()
def get_recipes():
    logging.info("Fetching all recipes")
    """Get all recipes"""
    try:
        user_id = get_jwt_identity()

        filters = {
            "title": request.args.get("title"),
            "ingredient": request.args.get("ingredient"),
            "course": request.args.get("course"),
            "cuisine": request.args.get("cuisine"),
            "primary_ingredient": request.args.get("primary-ingredient")
           
        }

        # Remove empty filters
        filters = {k: v for k, v in filters.items() if v}


        recipes = get_all_recipes(user_id, filters)

        if (recipes == [] or len(recipes) == 0) and (filters != {} and filters is not None):
            return jsonify({"msg": "Could not find any recipes matching your search.  Please refine your search."}), 200       
        elif (not recipes or len(recipes) == 0):
            return jsonify("204 strips any message, so it doesn't matter"), 204   
        return jsonify(recipes)
    except Exception as e:
        logging.error(f"Error fetching recipes: {e}")
        return jsonify({"error": "Failed to fetch recipes"}), 500

@recipes_bp.route('/recipe/<int:recipe_id>', methods=['GET'])
@jwt_required()
def get_recipe(recipe_id):
    logging.info(f"Fetching recipe with ID: {recipe_id}")
    """Get a single recipe by ID"""
    try:
        user_id = get_jwt_identity()
        # logging.info(f"User ID: {user_id}")
        recipe = get_recipe_by_id(recipe_id, user_id)
        if not recipe:
            return jsonify({"error": "Recipe not found"}), 404
        return jsonify(recipe)
    except Exception as e:
        logging.error(f"Error fetching recipe {recipe_id}: {e}")
        return jsonify({"error": "Failed to fetch recipe"}), 500

@recipes_bp.route('/recipe/<int:recipe_id>', methods=['PUT'])
@jwt_required()
def update_recipe(recipe_id):
    logging.info("Updating recipe")
    """Update a recipe"""
    try:
        user_id = get_jwt_identity()
        # logging.info(f"User ID: {user_id}")        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        updated_recipe = update_recipe_by_id(recipe_id, user_id, data)
        if not updated_recipe:
            return jsonify({"error": "Recipe not found"}), 404
        return jsonify(updated_recipe)
    except Exception as e:
        logging.error(f"Error updating recipe {recipe_id}: {e}")
        return jsonify({"error": "Failed to update recipe"}), 500

@recipes_bp.route('/recipe/<int:recipe_id>', methods=['DELETE'])
@jwt_required()
def delete_recipe(recipe_id):
    logging.info("Deleting recipe")
    """Delete a recipe"""
    try:
        user_id = get_jwt_identity()
        # logging.info(f"User ID: {user_id}")
        recipe = Recipe.query.filter_by(id=recipe_id, user_id=user_id).first()
        if not recipe:
            return jsonify({"error": "Recipe not found"}), 404
        db.session.delete(recipe)
        db.session.commit()
        return jsonify({"message": "Recipe deleted successfully"})
    except Exception as e:
        logging.error(f"Error deleting recipe {recipe_id}: {e}")
        return jsonify({"error": "Failed to delete recipe"}), 500


@recipes_bp.route('/job-status/<job_id>', methods=['GET'])
@jwt_required()
def job_status(job_id):
    """
    Poll the status of a background recipe import job.
 
    Returns:
        202  {"status": "pending"}               — still processing
        200  {"status": "completed", "recipe_id": …}  — finished, recipe is in DB
        500  {"status": "error", "error": "…"}   — something went wrong
        404  {"error": "Job not found"}           — bad/expired job_id
    """
    job = get_job(job_id)
    logging.info(f"Background upload for job {job_id}")

    if not job:
        return jsonify({"error": "Job not found"}), 404
    status = job["status"]
    if status == "pending":
        return jsonify(job), 202
    if status == "completed":
        return jsonify(job), 200
    return jsonify(job), 500


@recipes_bp.route('/recipes/upload', methods=['POST'])
@jwt_required()
def upload_recipe():
    logging.info("Adding recipe from file")
    """Upload and parse a recipe file"""
    try:
        user_id = get_jwt_identity()
        # logging.info(f"User ID: {user_id}")
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

        job_id = create_job()
        app = current_app._get_current_object()

        def run():
            try:
                # Extract text based on type
                ext = os.path.splitext(filename)[1].lower()
                if ext in {'.jpg', '.jpeg', '.png'}:
                    text = extract_text_from_image(file_path)
                elif ext == '.pdf':
                    text = extract_text_from_pdf(file_path, filename)
                else:  # .txt
                    text = parse_from_file(file_path, filename)

                recipe_data = parse_recipe_text(text, recipe_source=filename, is_file=True)

                with app.app_context():
                    recipe_id = save_recipe(recipe_data, user_id=user_id)                

                set_result(job_id, {
                    "recipe_id": recipe_id,
                    "title": recipe_data.get("title", "Untitled"),
                })

            except Exception as e:
                logging.error(f"Background upload failed for job {job_id}: {e}")
                set_error(job_id, str(e))

            finally:
                # Always clean up uploaded file
                try:
                    if os.path.exists(file_path):
                        logging.info("Deleting local file")
                        os.remove(file_path)
                except Exception as cleanup_error:
                    logging.warning(f"Failed to delete temp file {file_path}: {cleanup_error}")
        threading.Thread(target=run, daemon=True).start()
    
        return jsonify({"job_id": job_id}), 202                    

    except Exception as e:
            logging.error(f"Upload failed: {e}")
            return jsonify({"error": "Failed to process upload"}), 500        


@recipes_bp.route('/recipes/from-url', methods=['POST'])
@jwt_required()
def add_from_url():
    logging.info("Adding recipe from URL")
    """Add recipe by scraping a URL"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        url = data.get('url')
        if not url:
            return jsonify({"error": "No URL provided"}), 400
        
        job_id = create_job()
        logging.info("1")
        app = current_app._get_current_object()

        def run():
            try:
                print("31")
                scraped_text = scrape_url(url)
                if not scraped_text.strip():
                    raise Exception("Could not extract text from URL")
                # logging.info("Parsing recipe from URL")
                recipe_data = parse_recipe_text(scraped_text, recipe_source=url, is_file=False)
                logging.info("3")
                with app.app_context():
                    recipe_id = save_recipe(recipe_data, user_id=user_id) 
                
                set_result(job_id, {
                    "recipe_id": recipe_id,
                    "title": recipe_data.get("title", "Untitled"),
                })

            except Exception as e:
                err_str = str(e)
                logging.error(f"Background URL import failed for job {job_id}: {e}")
    
                if 'Failed to scrape URL: 402 Client Error:' in err_str:
                    set_error(job_id, "Website prevents scraping, print to PDF and upload as a file.")
                    # return jsonify({"error": "Website prevents scraping, print to PDF and upload as a file."}), 402
                elif 'Failed to scrape URL: 403 Client Error' in err_str:
                    set_error(job_id, "Website prevents scraping, print to PDF and upload as a file.")
                else:
                    set_error(job_id, err_str)
                    # return jsonify({"error": "Failed to import from URL"}), 500
 
        threading.Thread(target=run, daemon=True).start()
    
        return jsonify({"job_id": job_id}), 202

    except HTTPError as http_err:
            status_code = http_err.response.status_code
            if status_code == 402:
                # Payment Required — most likely quota/credits exhausted on your scraping service
                logging.info(f"Payment Required (402) — API/scraping service blocked")
                return jsonify({"error": "Scraping blocked, logging.info to PDF and upload."}), 402

    except Exception as e:
        if 'Failed to scrape URL: 402 Client Error:' in str(e):
            logging.info(f"URL import failed: Payment Required (402) — API/scraping service blocked, fullerror text: {e}")
            return jsonify({"error": "Website prevents scraping, print to PDF and upload as a file."}), 402
        logging.error(f"URL import failed: {e}")
        return jsonify({"error": "Failed to import from URL"}), 500