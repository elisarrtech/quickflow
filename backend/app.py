### app.py

from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import jwt

# Cargar variables de entorno si no estamos en Render
if os.environ.get("RENDER") != "true":
    from dotenv import load_dotenv
    load_dotenv()

# Inicializar la app
app = Flask(__name__)

# Configuración CORS para permitir llamadas desde Netlify
CORS(app, origins=["https://peppy-starlight-fd4c37.netlify.app"], supports_credentials=True)

# Configurar MongoDB y secret key
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "clave_supersecreta")

mongo = PyMongo(app)
app.mongo = mongo

# Verificar conexión MongoDB
try:
    mongo.cx.server_info()
    print("✅ Conectado a MongoDB Atlas")
except Exception as e:
    print("❌ Error al conectar a MongoDB:", e)

# Blueprints
from backend.routes.auth import auth_bp
from backend.routes.tasks import tasks_bp

app.register_blueprint(auth_bp, url_prefix="/api")
app.register_blueprint(tasks_bp, url_prefix="/api/tasks")

@app.route("/")
def home():
    return "API Quickflow funcionando ✅"



# --- MAIN LOCAL ---
if __name__ == "__main__":
    app.run(debug=True, port=5000)

