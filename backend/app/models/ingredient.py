from ..extensions import db
from datetime import datetime, timezone
from flask_jwt_extended import get_jwt_identity

class Ingredient(db.Model):
    __tablename__ = 'ingredients'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'))
    ingredient = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.String(50))
    unit = db.Column(db.String(50))

    recipe = db.relationship("Recipe", back_populates="ingredients")