from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_pymongo import PyMongo
import os

# --- Cargar variables de entorno si estás en local ---
if os.environ.get("RENDER") != "true":
    from dotenv import load_dotenv
    load_dotenv()

app = Flask(__name__)  # ✅ Instancia de Flask

# ✅ CORS solo una vez
CORS(app,
     origins=["https://peppy-starlight-fd4c37.netlify.app"],
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

# --- Configuración MongoDB ---
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "clave_supersecreta")
mongo = PyMongo(app)
app.mongo = mongo

# --- Verificar conexión ---
try:
    mongo.cx.server_info()
    print("✅ Conectado a MongoDB Atlas")
except Exception as e:
    print("❌ Error al conectar a MongoDB:", e)

# ✅ Ruta para archivos subidos
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(os.path.join(os.getcwd(), 'uploads'), filename)

# --- Importar Blueprints ---
from backend.routes.auth import auth_bp
from backend.routes.tasks import tasks_bp
from backend.routes.perfil import perfil_bp
from backend.routes.eventos_routes import eventos_bp
from backend.alerts import alerts_bp

# --- Registrar Blueprints ---
app.register_blueprint(eventos_bp)
app.register_blueprint(alerts_bp)
app.register_blueprint(auth_bp, url_prefix="/api")
app.register_blueprint(tasks_bp, url_prefix="/api")
app.register_blueprint(perfil_bp, url_prefix="/api")

# --- Ruta raíz ---
@app.route("/")
def home():
    return "API Quickflow funcionando ✅"

# --- Para correr local ---
if __name__ == "__main__":
    app.run(debug=True, port=5000)
