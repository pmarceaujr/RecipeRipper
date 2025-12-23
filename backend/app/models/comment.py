from ..extensions import db
from datetime import datetime, timezone
from flask_jwt_extended import get_jwt_identity

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'))
    comments = db.Column(db.Text, nullable=True)

    recipe = db.relationship("Recipe", back_populates="comments")