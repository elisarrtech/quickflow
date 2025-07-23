from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import jwt

# --- Cargar variables de entorno si no estamos en Render ---
if os.environ.get("RENDER") != "true":
    from dotenv import load_dotenv
    load_dotenv()

# --- Inicializar la app ---
app = Flask(__name__)

# --- Configuración CORS (después de inicializar Flask)
CORS(app,
     origins=["https://peppy-starlight-fd4c37.netlify.app"],
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

# --- Configurar MongoDB y Secret Key ---
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "clave_supersecreta")

mongo = PyMongo(app)
app.mongo = mongo  # Hacer accesible globalmente


# --- Verificar conexión a MongoDB ---
try:
    mongo.cx.server_info()
    print("✅ Conectado a MongoDB Atlas")
except Exception as e:
    print("❌ Error al conectar a MongoDB:", e)

# --- Importar y registrar Blueprints ---
from backend.routes.auth import auth_bp
from backend.routes.tasks import tasks_bp

app.register_blueprint(auth_bp, url_prefix="/api")
app.register_blueprint(tasks_bp, url_prefix="/api")  # <== ✅ corregido aquí

# --- Ruta de prueba ---
@app.route("/")
def home():
    return "API Quickflow funcionando ✅"

# --- Ejecución local ---
if __name__ == "__main__":
    app.run(debug=True, port=5000)
