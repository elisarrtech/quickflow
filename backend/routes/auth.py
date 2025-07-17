from flask import Blueprint, request, jsonify
from backend.jwt_utils import hash_password, check_password, generate_token
from flask_pymongo import ObjectId
from flask import current_app as app

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email y contraseña son requeridos"}), 400

    mongo = app.mongo
    if mongo.db.users.find_one({"email": email}):
        return jsonify({"message": "Usuario ya registrado"}), 409

    hashed_password = hash_password(password)
    nuevo_usuario = {
        "email": email,
        "password": hashed_password
    }

    mongo.db.users.insert_one(nuevo_usuario)
    return jsonify({"message": "Usuario registrado exitosamente ✅"}), 201


@auth_bp.route("/login", methods=["POST"])
def login_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    mongo = app.mongo
    user = mongo.db.users.find_one({"email": email})

    if user and check_password(user.get("password"), password):
        token = generate_token(user.get("email"))
        return jsonify({"token": token}), 200
    else:
        return jsonify({"message": "Credenciales inválidas"}), 401
