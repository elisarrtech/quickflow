# backend/routes/auth.py
from flask import Blueprint, request, jsonify, current_app
from backend.jwt_utils import hash_password, check_password, generate_token
import re

auth_bp = Blueprint("auth", __name__)

def es_email_valido(email):
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None

@auth_bp.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    if not email or not password:
        return jsonify({"error": "Email y contraseña son requeridos"}), 400

    if not es_email_valido(email):
        return jsonify({"error": "Formato de email inválido"}), 400

    if len(password) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400

    try:
        # ✅ CORREGIDO: Usa current_app
        mongo = current_app.mongo.db
        if mongo.users.find_one({"email": email}):
            return jsonify({"error": "Usuario ya registrado"}), 409

        hashed_password = hash_password(password)
        nuevo_usuario = {
            "email": email,
            "password": hashed_password
        }

        result = mongo.users.insert_one(nuevo_usuario)
        user_id = str(result.inserted_id)

        return jsonify({
            "message": "Usuario registrado exitosamente ✅",
            "user": {
                "id": user_id,
                "email": email
            }
        }), 201

    except Exception as e:
        current_app.logger.error(f"❌ Error en registro: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@auth_bp.route("/login", methods=["POST"])
def login_user():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    if not email or not password:
        return jsonify({"error": "Email y contraseña son requeridos"}), 400

    try:
        # ✅ CORREGIDO: Usa current_app
        mongo = current_app.mongo.db
        user = mongo.users.find_one({"email": email})

        if user and check_password(user["password"], password):
            token = generate_token(user["email"])
            return jsonify({
                "token": token,
                "user": {
                    "id": str(user["_id"]),
                    "email": user["email"]
                }
            }), 200
        else:
            return jsonify({"error": "Credenciales inválidas"}), 401

    except Exception as e:
        current_app.logger.error(f"❌ Error en login: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500
