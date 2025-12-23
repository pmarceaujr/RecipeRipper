from ..extensions import db
from datetime import datetime, timezone
from flask_jwt_extended import get_jwt_identity

class Recipe(db.Model):
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)    
    title = db.Column(db.String(255), nullable=False)
    course = db.Column(db.String(100))
    cuisine = db.Column(db.String(100))
    prep_time = db.Column(db.String(100))
    cook_time = db.Column(db.String(100))
    servings = db.Column(db.String(100))
    total_time = db.Column(db.String(100))
    primary_ingredient = db.Column(db.String(100))
    is_url = db.Column(db.Integer, default=0)
    recipe_source = db.Column(db.Text)
    click_count = db.Column(db.Integer, default=0)
    rating = db.Column(db.Integer, default=0)


    
    ingredients = db.relationship("Ingredient", back_populates="recipe", cascade="all, delete-orphan")
    directions = db.relationship("Direction", back_populates="recipe", cascade="all, delete-orphan")
    comments = db.relationship("Comment", back_populates="recipe", cascade="all, delete-orphan")