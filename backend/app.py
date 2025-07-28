from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
import os

# --- Inicializar Flask ---
app = Flask(__name__)

# --- Configuración CORS (CORREGIDA) ---
CORS(app,
     origins="https://peppy-starlight-fd4c37.netlify.app",  # ✅ Sin espacios
     supports_credentials=False,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"],
     expose_headers=["Content-Type", "Authorization"])

# --- Configuración MongoDB ---
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "clave_supersecreta")

mongo = PyMongo(app)
app.mongo = mongo

# --- Verificar conexión a MongoDB ---
try:
    mongo.cx.server_info()
    print("✅ Conectado a MongoDB Atlas")
except Exception as e:
    print("❌ Error al conectar a MongoDB:", e)

# --- Logging para debugging ---
@app.before_request
def log_request_info():
    print(f"👉 Método: {request.method} | Ruta: {request.path}")
    print(f"👉 Origin: {request.headers.get('Origin')}")
    print(f"👉 Headers: {dict(request.headers)}")

# --- Ruta para servir archivos subidos ---
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(os.path.join(os.getcwd(), 'uploads'), filename)

# --- Importar y registrar Blueprints ---
from backend.routes.auth import auth_bp
from backend.routes.tasks import tasks_bp
from backend.routes.perfil import perfil_bp
from backend.routes.eventos_routes import eventos_bp
from backend.routes.alerts_routes import alerts_bp

app.register_blueprint(auth_bp, url_prefix="/api")
app.register_blueprint(tasks_bp, url_prefix="/api")
app.register_blueprint(perfil_bp, url_prefix="/api")
app.register_blueprint(eventos_bp, url_prefix="/api")
app.register_blueprint(alerts_bp, url_prefix="/api")

# --- Ruta raíz ---
@app.route("/")
def home():
    return "API Quickflow funcionando ✅"

# --- Ejecutar ---
if __name__ == "__main__":
    app.run(debug=True, port=5000)
