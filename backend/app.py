from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import jwt

# --- CARGAR VARIABLES DE ENTORNO ---
if os.environ.get("RENDER") != "true":
    from dotenv import load_dotenv
    load_dotenv()

# --- CONFIGURACIÓN FLASK ---
app = Flask(__name__)

# ✅ CORS robusto (Netlify o abierto para desarrollo)
CORS(app, resources={r"/api/*": {"origins": "https://peppy-starlight-fd4c37.netlify.app"}}, supports_credentials=True)

# --- CONFIGURACIÓN MONGO ---
MONGO_URI = os.getenv("MONGO_URI")
SECRET_KEY = os.getenv("SECRET_KEY", "supersecreto")

if not MONGO_URI:
    print("❌ MONGO_URI no definido")
    mongo = None
else:
    app.config["MONGO_URI"] = MONGO_URI
    mongo = PyMongo(app)
    try:
        mongo.cx.server_info()
        print("✅ Conectado a MongoDB Atlas")
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        mongo = None

app.mongo = mongo

# --- BLUEPRINTS ---
from backend.routes.tasks import tasks_bp
app.register_blueprint(tasks_bp, url_prefix="/api/tasks")

# --- RUTAS DE AUTENTICACIÓN ---
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not mongo or not mongo.db:
        return jsonify({"error": "Error de base de datos"}), 500

    users = mongo.db.users
    if users.find_one({"email": email}):
        return jsonify({"error": "Correo ya registrado"}), 400

    users.insert_one({"email": email, "password": password})
    return jsonify({"message": "Registro exitoso"}), 201

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not mongo or not mongo.db:
        return jsonify({"error": "Error de base de datos"}), 500

    users = mongo.db.users
    user = users.find_one({"email": email})

    if not user or user.get("password") != password:
        return jsonify({"error": "Credenciales inválidas"}), 401

    token = jwt.encode({
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=2)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({"token": token})

@app.route("/", methods=["GET"])
def index():
    return "✅ API funcionando correctamente"

# --- MAIN LOCAL ---
if __name__ == "__main__":
    app.run(debug=True, port=5000)
