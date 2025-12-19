from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import recipe_parser
import database

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend



# Configure upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

@app.route('/')
def home():
    return jsonify({"message": "Recipe Database API", "status": "running"})

@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    """Get all recipes"""
    try:
        recipes = database.get_all_recipes()
        return jsonify(recipes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/recipes/upload', methods=['POST'])
def upload_recipe():
    """Upload a recipe file (supports TXT, PDF, JPG, PNG)"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Check file extension
        allowed_extensions = ['.txt', '.pdf', '.jpg', '.jpeg', '.png']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            return jsonify({"error": f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"}), 400
        
        # Save file temporarily
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        try:
            # Parse recipe based on file type
            if file_extension in ['.jpg', '.jpeg', '.png']:
                exdtracted_text = recipe_parser.extract_text_from_image(file_path)
            elif file_extension in ['.pdf']:
                print("In PDF IF")
                extracted_text = recipe_parser.extract_text_from_pdf(file_path, file.filename)
                print("Passed PDF IF")
            else:
                extracted_text = recipe_parser.parse_from_file(file_path, file.filename)

            # Save to database
            recipe_data = recipe_parser.parse_recipe_text(extracted_text)
            recipe_id = database.save_recipe(recipe_data)
            
            return jsonify({
                "message": "Recipe added successfully",
                "recipe_id": recipe_id,
                "title": recipe_data.get('title')
            })
        finally:
            # Clean up uploaded file
            print("Done!")
        #     if os.path.exists(file_path):
        #         os.remove(file_path)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/recipes/from-url', methods=['POST'])
def add_from_url():
    """Add recipe from URL"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({"error": "No URL provided"}), 400
        
        # Scrape URL
        scraped_text = recipe_parser.scrape_url(url)
        
        # Parse recipe
        recipe_data = recipe_parser.parse_recipe_text(scraped_text, source_url=url)
        
        # Save to database
        recipe_id = database.save_recipe(recipe_data)
        
        return jsonify({
            "message": "Recipe added successfully",
            "recipe_id": recipe_id,
            "title": recipe_data.get('title')
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/recipes/<int:recipe_id>', methods=['DELETE'])
def delete_recipe(recipe_id):
    """Delete a recipe"""
    try:
        session = database.get_session()
        recipe = session.query(database.Recipe).get(recipe_id)
        if recipe:
            session.delete(recipe)
            session.commit()
            session.close()
            return jsonify({"message": "Recipe deleted"})
        else:
            session.close()
            return jsonify({"error": "Recipe not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)