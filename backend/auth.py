from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta

auth_bp = Blueprint("auth", __name__)

def get_users_collection():
    return current_app.mongo.db.users

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Correo y contraseña requeridos"}), 400

    users = get_users_collection()
    if users.find_one({"email": email}):
        return jsonify({"error": "El correo ya está registrado"}), 400

    hashed_password = generate_password_hash(password)
    users.insert_one({"email": email, "password": hashed_password})

    return jsonify({"message": "Registro exitoso"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    users = get_users_collection()
    user = users.find_one({"email": email})

    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Credenciales inválidas"}), 401

    token = jwt.encode({
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=2)
    }, current_app.config["SECRET_KEY"], algorithm="HS256")

    return jsonify({"token": token})
