from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

class Recipe(Base):
    __tablename__ = 'recipes'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    classification = Column(String(100))
    primary_ingredient = Column(String(100))
    is_url = Column(Integer, default=0)
    recipe_source = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    ingredients = relationship("Ingredient", back_populates="recipe", cascade="all, delete-orphan")
    directions = relationship("Direction", back_populates="recipe", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="recipe", cascade="all, delete-orphan")

class Ingredient(Base):
    __tablename__ = 'ingredients'
    
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    ingredient = Column(Text, nullable=False)
    quantity = Column(String(50))
    unit = Column(String(50))
    
    recipe = relationship("Recipe", back_populates="ingredients")

class Direction(Base):
    __tablename__ = 'directions'
    
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    step_number = Column(Integer)
    instruction = Column(Text, nullable=False)
    
    recipe = relationship("Recipe", back_populates="directions")

class Comment(Base):
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    comments = Column(Text, nullable=True)
    
    recipe = relationship("Recipe", back_populates="comments")

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///recipes.db')

# Heroku fix for postgres:// vs postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def get_session():
    return Session()

def save_recipe(recipe_data):
    print("Inside save_recipe function")
    """Save a parsed recipe to the database"""
    session = get_session()
    
    try:
        print("Inside save_recipe try function")
        # Create recipe
        recipe = Recipe(
            title=recipe_data['title'],
            classification=recipe_data.get('classification', 'Uncategorized'),
            primary_ingredient=recipe_data.get('primary_ingredient', 'Unknown'),
            is_url=recipe_data.get('is_url', 0),
            recipe_source=recipe_data.get('recipe_source')
        )
        session.add(recipe)
        session.flush()  # Get recipe.id
        
        # Add ingredients
        for ing in recipe_data.get('ingredients', []):
            ingredient = Ingredient(
                recipe_id=recipe.id,
                ingredient=ing.get('ingredient', ''),
                quantity=ing.get('quantity', ''),
                unit=ing.get('unit', '')
            )
            session.add(ingredient)
        
        # Add directions
        for dir_data in recipe_data.get('directions', []):
            direction = Direction(
                recipe_id=recipe.id,
                step_number=dir_data.get('step_number', 0),
                instruction=dir_data.get('instruction', '')
            )
            session.add(direction)

        # Add comments
            comments = Comment(
                recipe_id=recipe.id,
                comments=recipe_data.get('comments', '')
            )
            session.add(comments)

        session.commit()
        print("Exiting save_recipe function")
        return recipe.id
    except Exception as e:
        session.rollback()
        print(f"Error saving recipe: {e}")
        raise e
    finally:
        session.close()

def get_all_recipes():
    """Get all recipes with their ingredients and directions"""
    print("Inside get_all_recipes function")
    try:
        session = get_session()
        recipes = session.query(Recipe).all()
    except Exception as e:
        session.rollback()
        print(f"Error getting recipe: {e}")
        raise e        
    
    result = []
    try:
        print("Inside get_all_recipes try function")
        for recipe in recipes:
            recipe_dict = serialize_recipe(recipe)
            result.append(recipe_dict)
        
        # session.close()
        return result
    except Exception as e:
        session.rollback()
        print(f"Error getting recipe: {e}")
        raise e
    finally:
        session.close()

def get_recipe_by_id(recipe_id):
    """Get a recipe by ID"""
    print("Inside get_recipe_by_id function")
    try:
        session = get_session()
        recipe = session.query(Recipe).filter_by(id=recipe_id).first()
        print(f"Recipe found: {recipe}")
    except Exception as e:
        session.rollback()
        print(f"Error getting recipe: {e}")
        raise e        
    
    result = []
    try:
        print("Inside get_recipe_by_id try function")
        print(f"title: {recipe.title}")
        recipe_dict = serialize_recipe(recipe)

        return recipe_dict
    except Exception as e:
        session.rollback()
        print(f"Error getting recipe: {e}")
        raise e
    finally:
        session.close()        

def update_recipe(recipe_id, data):
    session = get_session()
    try:
        recipe = session.query(Recipe).filter_by(id=recipe_id).first()
        if not recipe:
            return None

        recipe.title = data.get("title", recipe.title)
        recipe.classification = data.get("classification", recipe.classification)
        recipe.primary_ingredient = data.get("primary_ingredient", recipe.primary_ingredient)
        recipe.recipe_source = data.get("recipe_source", recipe.recipe_source)
        recipe.is_url = data.get("is_url", recipe.is_url)

        # Remove old ingredients and directions
        session.query(Ingredient).filter_by(recipe_id=recipe.id).delete(synchronize_session=False)
        session.query(Direction).filter_by(recipe_id=recipe.id).delete(synchronize_session=False)
        session.query(Comment).filter_by(recipe_id=recipe.id).delete(synchronize_session=False)

        # --- Ingredients ---
        if "ingredients" in data:
            # Remove existing ingredients
            # for ing in recipe.ingredients:
            #     session.delete(ing)
            # session.flush()  # ensure deletion before adding new
            # Add new ingredients
            for ing_data in data["ingredients"]:
                new_ing = Ingredient(
                    recipe_id=recipe.id,
                    ingredient=ing_data.get("ingredient"),
                    quantity=ing_data.get("quantity"),
                    unit=ing_data.get("unit")
                )
                session.add(new_ing)

        # --- Directions ---
        if "directions" in data:
            # Remove existing directions
            # for d in recipe.directions:
            #     session.delete(d)
            # session.flush()
            # Add new directions
            for dir_data in data["directions"]:
                new_dir = Direction(
                    recipe_id=recipe.id,
                    step_number=dir_data.get("step_number"),
                    instruction=dir_data.get("instruction")
                )
                session.add(new_dir)

        # --- Comments ---
        if "comments" in data:
            # Remove existing comments
            # for c in recipe.comments:
            #     session.delete(c)
            # session.flush()
            # Add new comments
            for comment_data in data["comments"]:
                new_comment = Comment(
                    recipe_id=recipe.id,
                    comments=comment_data.get("comments")
                )
                session.add(new_comment)

        session.commit()
        recipe_dict = serialize_recipe(recipe)
        return recipe_dict 
    except:
        session.rollback()
        raise
    finally:
        session.close()



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
    return {
        "id": recipe.id,
        "title": recipe.title,
        "classification": recipe.classification,
        "primary_ingredient": recipe.primary_ingredient,
        "is_url": recipe.is_url,
        "recipe_source": recipe.recipe_source,
        "created_at": recipe.created_at.isoformat() if recipe.created_at else None,
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