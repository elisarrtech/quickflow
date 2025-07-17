from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import os
import jwt

# --- CARGAR VARIABLES DE ENTORNO SI NO ES DEPLOY EN RENDER ---
if os.environ.get("RENDER") != "true":
    from dotenv import load_dotenv
    load_dotenv()

# --- CONFIGURACIÓN DE LA APLICACIÓN ---
app = Flask(__name__)

# ✅ CORS GLOBAL (Frontend Netlify)
CORS(app, origins=["https://peppy-starlight-fd4c37.netlify.app"], supports_credentials=True)

# --- CONFIGURACIÓN DE MONGO Y SECRET_KEY ---
MONGO_URI = os.getenv("MONGO_URI")
SECRET_KEY = os.getenv("SECRET_KEY", "supersecreto")

if not MONGO_URI:
    print("❌ MONGO_URI no está definido")
    mongo = None
else:
    app.config["MONGO_URI"] = MONGO_URI
    mongo = PyMongo(app)

    try:
        mongo.cx.server_info()
        print("✅ Conectado exitosamente a MongoDB Atlas")
    except Exception as e:
        print(f"❌ Error al conectar a MongoDB Atlas: {e}")
        mongo = None

# --- Hacer mongo accesible globalmente ---
app.mongo = mongo

# --- IMPORTAR Y REGISTRAR BLUEPRINTS ---
from backend.routes.tasks import tasks_bp
from flask_cors import CORS as BlueprintCORS  # para usarlo en blueprints también

# ✅ CORS SOBRE EL BLUEPRINT (muy importante para tareas)
BlueprintCORS(tasks_bp, origins="https://peppy-starlight-fd4c37.netlify.app", supports_credentials=True)

app.register_blueprint(tasks_bp, url_prefix="/api/tasks")

# --- RUTA DE PRUEBA ---
@app.route("/")
def home():
    return "API funcionando correctamente ✅"

# --- REGISTRO DE USUARIO ---
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if mongo is None or mongo.db is None:
        return jsonify({"error": "Error de conexión con la base de datos"}), 500

    users = mongo.db.users
    if users.find_one({"email": email}):
        return jsonify({"error": "El correo ya está registrado"}), 400

    users.insert_one({"email": email, "password": password})
    return jsonify({"message": "Registro exitoso"}), 201

# --- INICIO DE SESIÓN ---
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if mongo is None or mongo.db is None:
        return jsonify({"error": "Error de conexión con la base de datos"}), 500

    users = mongo.db.users
    user = users.find_one({"email": email})

    if not user or user.get("password") != password:
        return jsonify({"error": "Credenciales inválidas"}), 401

    token = jwt.encode({
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=2)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({"token": token})

# --- MAIN LOCAL ---
if __name__ == "__main__":
    app.run(debug=True, port=5000)
