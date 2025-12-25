# app/auth/routes.py
from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.user import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_mail import Mail, Message  # For reset

auth_bp = Blueprint('auth', __name__)
mail = Mail()  # Init in factory if needed

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'msg': 'Email exists'}), 400
    user = User(username=data['username'], 
                email=data['email'],
                first_name=data['firstname'], 
                last_name=data['lastname'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'msg': 'Registered'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    user_id = str(user.id)
    if user and user.check_password(data['password']):
        token = create_access_token(identity=user_id)
        return jsonify(access_token=token)
    return jsonify({'msg': 'Bad credentials'}), 401

# Password reset: /forgot → generate token, email link
# /reset/<token> → validate and update
# See Flask-JWT-Extended docs for protected reset tokens

def get_current_user():
    user_id = get_jwt_identity()
    return User.query.get(user_id)