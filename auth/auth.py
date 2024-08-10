# auth.py
from flask import Blueprint, request, jsonify, current_app, make_response, url_for
from werkzeug.security import generate_password_hash, check_password_hash
# from flask_jwt_extended import create_access_token, jwt_required, 
# get_jwt_identity, unset_jwt_cookies, set_access_cookies
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies, set_access_cookies
from datetime import timedelta
from bson import ObjectId
from flask_mail import Message
import re
from utils.utils import generate_reset_token, verify_reset_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({"message": "Username and password are required"}), 400
        existing_user = current_app.mongo.db.users.find_one({'username': username, 'email': email})
        if existing_user:
            return jsonify({"message": "User already exists"}), 400

        hashed_password = generate_password_hash(password)
        current_app.mongo.db.users.insert_one({'username': username, 'email':email, 'password': hashed_password})

        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
          return jsonify({"message": str(e)}), 500

@auth_bp.route('/signin', methods=['POST'])
def signin():
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"message": "Email and password are required"}), 400

        user = current_app.mongo.db.users.find_one({'email': email})
        if not user or not check_password_hash(user['password'], password):
            return jsonify({"message": "Invalid email or password"}), 401

        access_token = create_access_token(identity=str(user['_id']), expires_delta=timedelta(days=2))
        response = make_response(jsonify({"message": "You are logged in successfully"}))
        # response.set_cookie('access_token', access_token, httponly=True)
        set_access_cookies(response, access_token)
        return response
    except Exception as e:
          return jsonify({"message": str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    try:
        user_id = get_jwt_identity()
        user = current_app.mongo.db.users.find_one({'_id': ObjectId(user_id)})

        if not user:
            return jsonify({"message": "User not found"}), 404
        user['_id'] = str(user['_id'])
        return jsonify({"user": user})
    except Exception as e:
          return jsonify({"message": str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        response = make_response(jsonify({"message": "You are logged out successfully"}))
        # response.set_cookie('access_token', '', expires=0)
        unset_jwt_cookies(response)
        return response
    except Exception as e:
          return jsonify({"message": str(e)}), 500

@auth_bp.route('/forget_password', methods=['POST'])
def forget_password():
    try:
        data = request.json
        email = data.get('email')

        if not email:
            return jsonify({"message": "Email is required"}), 400

        user = current_app.mongo.db.users.find_one({'email': email})
        if not user:
            return jsonify({"message": "User not found"}), 404

        token = generate_reset_token(user['email'])
        reset_url = url_for('auth.reset_with_token', token=token, _external=True)
        msg = Message(subject="Password Reset Request",
                      sender=current_app.config['MAIL_DEFAULT_SENDER'],
                      recipients=[user['email']],
                      body=f"To reset your password, click the following link: {reset_url}")

        current_app.mail.send(msg)

        return jsonify({"message": "Password reset email sent", "token":token, "reset_url":reset_url}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@auth_bp.route('/reset_with_token/<token>', methods=['POST'])
def reset_with_token(token):
    try:
        email = verify_reset_token(token)
        if not email:
            return jsonify({"message": "Invalid or expired token"}), 400

        data = request.json
        new_password = data.get('new_password')

        if not new_password:
            return jsonify({"message": "New password is required"}), 400

        hashed_password = generate_password_hash(new_password)
        current_app.mongo.db.users.update_one(
            {'email': email},
            {'$set': {'password': hashed_password}}
        )

        return jsonify({"message": "Password reset successful"})
    except Exception as e:
        return jsonify({"message": str(e)}), 500
