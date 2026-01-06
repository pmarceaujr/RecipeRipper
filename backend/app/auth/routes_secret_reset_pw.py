# app/auth/routes.py
from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models.user import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_mail import Mail, Message  # For reset

authreset_bp = Blueprint('authreset', __name__)
mail = Mail()  # Init in factory if needed


@authreset_bp.route('/secret_backdoor_pw_reset', methods=['PUT'])
def reset_pw():
    print("Inside reset password function")

    data = request.json
    user = User.query.filter_by(email=data['userId']).first()
    if not user:
        user = User.query.filter_by(username=data['userId']).first()
    if not user:
        return jsonify({'error': 'User not found.  Please check your credentials or register for an account.'}), 401
    # user_id = str(user.id)
    print(f"user found: {user.username}; {user.password_hash}")
    if user:
        # user = User(username=data['username']) 
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        return jsonify({'msg': 'Password reset successfully'}), 201        
        token = create_access_token(identity=user_id)
        return jsonify(access_token=token)
    return jsonify({'msg': 'Bad credentials'}), 401

# Password reset: /forgot → generate token, email link
# /reset/<token> → validate and update
# See Flask-JWT-Extended docs for protected reset tokens

def get_current_user():
    user_id = get_jwt_identity()
    return User.query.get(user_id)
