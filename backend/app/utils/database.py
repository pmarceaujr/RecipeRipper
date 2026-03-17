from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from ..extensions import db
from ..models.recipe import Recipe
from ..models.ingredient import Ingredient
from ..models.direction import Direction
from ..models.comment import Comment
from datetime import datetime
import os

# # Database setup
# DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///recipes.db')

# # Heroku fix for postgres:// vs postgresql://
# if DATABASE_URL.startswith('postgres://'):
#     DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# engine = create_engine(DATABASE_URL)
# Base.metadata.create_all(engine)
# Session = sessionmaker(bind=engine)

# def get_session():
#     return Session()

def save_recipe(recipe_data, user_id):
    print("Inside save_recipe function")
    """Save a parsed recipe to the database"""
    try:
        print("Inside save_recipe try function")
        # Create recipe
        recipe = Recipe(
            title=recipe_data['title'],
            user_id=user_id,
            course=recipe_data.get('course', 'Uncategorized'),
            cuisine=recipe_data.get('cuisine', 'Unknown'),
            prep_time=recipe_data.get('prep_time', 'Unknown'),
            cook_time=recipe_data.get('cook_time', 'Unknown'),
            servings=recipe_data.get('servings', 'Unknown'),
            total_time=recipe_data.get('total_time', 'Unknown'),
            primary_ingredient=recipe_data.get('primary_ingredient', 'Unknown'),
            is_url=recipe_data.get('is_url', 0),
            recipe_source=recipe_data.get('recipe_source')
        )
        db.session.add(recipe)
        db.session.flush()  # Get recipe.id

        # Add ingredients
        for ing in recipe_data.get('ingredients', []):
            ingredient = Ingredient(
                recipe_id=recipe.id,
                ingredient=ing.get('ingredient', ''),
                quantity=ing.get('quantity', ''),
                unit=ing.get('unit', '')
            )
            db.session.add(ingredient)
        
        # Add directions
        for dir_data in recipe_data.get('directions', []):
            direction = Direction(
                recipe_id=recipe.id,
                step_number=dir_data.get('step_number', 0),
                instruction=dir_data.get('instruction', '')
            )
            db.session.add(direction)

        # Add comments
            comments = Comment(
                recipe_id=recipe.id,
                comments=recipe_data.get('comments', '')
            )
            if recipe_data.get('comments'):
                db.session.add(comments)

        db.session.commit()
        print("Exiting save_recipe function")
        return recipe.id
    except Exception as e:
        db.session.rollback()
        print(f"Error saving recipe: {e}")
        raise e


def get_all_recipes(user_id):
    """Get all recipes with their ingredients and directions"""
    print("Inside get_all_recipes function")
    # user_id_= int(user_id)
    try:
        recipe_data = Recipe.query.filter_by(user_id=user_id).order_by(Recipe.created_at.desc())
        if recipe_data is not None:
            result = []
            for recipe in recipe_data:
                recipe_dict = serialize_recipe(recipe)
                result.append(recipe_dict)
            return result
        else:
            return recipe_data

    except Exception as e:
        print(f"Error getting recipe: {e}")
        raise e


def get_recipe_by_id(recipe_id, user_id):
    """Get a recipe by ID"""
    print("Inside get_recipe_by_id function")
    recipe_data = Recipe.query.filter_by(id=recipe_id, user_id=user_id).first()      

    result = []
    try:
        recipe_dict = serialize_recipe(recipe_data)
        return recipe_dict
    except Exception as e:
        print(f"Error getting recipe: {e}")
        raise e

def update_recipe_by_id(recipe_id, user_id, data):
    print("Inside update_recipe function")
    try:
        recipe = Recipe.query.filter_by(id=recipe_id, user_id=user_id).first()
        if not recipe:
            return None
        print("Inside update_recipe try function")
        recipe.title = data.get("title", recipe.title)
        recipe.course = data.get("course", recipe.course)
        recipe.cuisine = data.get("cuisine", recipe.cuisine)
        recipe.prep_time = data.get("prep_time", recipe.prep_time)
        recipe.cook_time = data.get("cook_time", recipe.cook_time)
        recipe.total_time = data.get("total_time", recipe.total_time)
        recipe.servings = data.get("servings", recipe.servings)
        recipe.primary_ingredient = data.get("primary_ingredient", recipe.primary_ingredient)
        recipe.recipe_source = data.get("recipe_source", recipe.recipe_source)
        recipe.is_url = data.get("is_url", recipe.is_url)
        print("Before db.session.add")
        # Remove old ingredients and directions
        db.session.query(Ingredient).filter_by(recipe_id=recipe.id).delete(synchronize_session=False)
        db.session.query(Direction).filter_by(recipe_id=recipe.id).delete(synchronize_session=False)
        db.session.query(Comment).filter_by(recipe_id=recipe.id).delete(synchronize_session=False)
        print("Before db.session.commit")
        # --- Ingredients ---
        if "ingredients" in data:
            print("Inside update_recipe ingredients function")
            # Add new ingredients
            for ing_data in data["ingredients"]:
                new_ing = Ingredient(
                    recipe_id=recipe.id,
                    ingredient=ing_data.get("ingredient"),
                    quantity=ing_data.get("quantity"),
                    unit=ing_data.get("unit")
                )
                db.session.add(new_ing)

        # --- Directions ---
        if "directions" in data:
            print("Inside update_recipe directions function")
            # Add new directions
            for dir_data in data["directions"]:
                new_dir = Direction(
                    recipe_id=recipe.id,
                    step_number=dir_data.get("step_number"),
                    instruction=dir_data.get("instruction")
                )
                db.session.add(new_dir)

        # --- Comments ---
        if "comments" in data:
            print("Inside update_recipe comments function")
           # Add new comments
            for comment_data in data["comments"]:
                new_comment = Comment(
                    recipe_id=recipe.id,
                    comments=comment_data.get("comments")
                )
                db.session.add(new_comment)

        db.session.commit()
        recipe_dict = serialize_recipe(recipe)
        return recipe_dict 
    except:
        db.session.rollback()
        raise




def delete_recipe(recipe_id):
    session = get_session()
    try:
        recipe = session.query(Recipe).filter_by(id=recipe_id).first()
        if not recipe:
            return False

        session.delete(recipe)
        session.commit()
        return True
    except:
        session.rollback()
        raise
    finally:
        session.close()


def serialize_recipe(recipe):
    print("Inside serialize_recipe function")

    # Safely convert created_at 
    created_at = recipe.created_at 
    if isinstance(created_at, str): 
        try: 
            created_at = datetime.fromisoformat(created_at) 
        except ValueError: created_at = None

    return {
        "id": recipe.id,
        "title": recipe.title,
        "course": recipe.course,
        "cuisine": recipe.cuisine,
        "prep_time": recipe.prep_time,
        "cook_time": recipe.cook_time,
        "total_time": recipe.total_time,
        "servings": recipe.servings,
        "primary_ingredient": recipe.primary_ingredient,
        "is_url": recipe.is_url,
        "recipe_source": recipe.recipe_source,
        "created_at": created_at.isoformat() if created_at else None,
        "ingredients": [
            {"ingredient": i.ingredient, "quantity": i.quantity, "unit": i.unit}
            for i in getattr(recipe, "ingredients", [])
        ],
        "directions": sorted(
            [{"step_number": d.step_number, "instruction": d.instruction}
             for d in getattr(recipe, "directions", [])],
            key=lambda x: x["step_number"]
        ),
        "comments": [{"comments": c.comments} for c in getattr(recipe, "comments", [])]
    }