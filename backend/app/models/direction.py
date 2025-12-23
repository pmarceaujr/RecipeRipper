from ..extensions import db
from datetime import datetime, timezone
from flask_jwt_extended import get_jwt_identity

class Direction(db.Model):
    __tablename__ = 'directions'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'))
    step_number = db.Column(db.Integer)
    instruction = db.Column(db.Text, nullable=False)

    recipe = db.relationship("Recipe", back_populates="directions")