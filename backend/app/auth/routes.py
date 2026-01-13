# app/auth/routes.py
from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.user import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_mail import Mail, Message  # For reset
import os
import requests

auth_bp = Blueprint('auth', __name__)
mail = Mail()  # Init in factory if needed

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json

    # Extract token
    token = data.get('recaptchaToken')
    if not token:
        return jsonify({'error': 'Missing reCAPTCHA token'}), 400    

    # Verify with Google
    secret_key = os.getenv('RECAPTCHA_SECRET_KEY')
    verify_url = 'https://www.google.com/recaptcha/api/siteverify'
    response = requests.post(verify_url, data={
        'secret': secret_key,
        'response': token,
    })
    result = response.json()

    if not result.get('success') or result.get('score', 0) < 0.5:  # Score threshold: 0.5 is medium; adjust if needed (1.0 = human, 0.0 = bot)
        return jsonify({'error': 'reCAPTCHA verification failed. Are you a bot?'}), 400


    existing_user = User.query.filter((User.username == data['username']) | (User.email == data['email'])).first()
    if existing_user:
        if existing_user.email == data['email']:
            return jsonify({'error': 'Email already in use, please use a different email'}), 409
        if existing_user.username == data['username']:
            return jsonify({'error': 'Username already in use, please use a different username'}), 409
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
    print("Inside login function")
    data = request.json
    user = User.query.filter_by(email=data['userId']).first()
    if not user:
        user = User.query.filter_by(username=data['userId']).first()
    if not user:
        return jsonify({'error': 'User not found.  Please check your credentials or register for an account.'}), 401
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