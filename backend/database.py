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
    source_url = Column(Text)
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
            source_url=recipe_data.get('source_url')
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
    session = get_session()
    recipes = session.query(Recipe).all()
    
    result = []
    for recipe in recipes:
        recipe_dict = {
            'id': recipe.id,
            'title': recipe.title,
            'classification': recipe.classification,
            'primary_ingredient': recipe.primary_ingredient,
            'source_url': recipe.source_url,
            'created_at': recipe.created_at.isoformat(),
            'ingredients': [
                {
                    'ingredient': ing.ingredient,
                    'quantity': ing.quantity,
                    'unit': ing.unit
                } for ing in recipe.ingredients
            ],
            'directions': [
                {
                    'step_number': dir.step_number,
                    'instruction': dir.instruction
                } for dir in sorted(recipe.directions, key=lambda x: x.step_number)
            ],
            'comments': [
                {
                    'comments': comment.comments
                } for comment in recipe.comments
            ]
        }
        result.append(recipe_dict)
    
    session.close()
    return result