from flask import Blueprint, request, jsonify, current_app
from backend.jwt_utils import generate_token
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Correo y contraseña son requeridos"}), 400

    db = current_app.mongo.db
    if db.users.find_one({"email": email}):
        return jsonify({"error": "El correo ya está registrado"}), 400

    hashed_password = generate_password_hash(password)
    db.users.insert_one({"email": email, "password": hashed_password})

    return jsonify({"message": "Registro exitoso"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Correo y contraseña requeridos"}), 400

    db = current_app.mongo.db
    user = db.users.find_one({"email": email})
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Credenciales inválidas"}), 401

    token = generate_token(email)
    return jsonify({"token": token})
