# app.py
from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
import os

# --- Inicializar Flask ---
app = Flask(__name__)

# --- Configuración MongoDB ---
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
if not app.config["MONGO_URI"]:
    raise ValueError("La variable MONGO_URI no está definida en el entorno")

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "clave_supersecreta")

# --- Configuración CORS (CORREGIDA) ---
CORS(app,
     origins=[
         "https://peppy-starlight-fd4c37.netlify.app",  # ✅ CORREGIDO: sin espacios
         "http://localhost:5173"
     ],
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "Origin"],
     expose_headers=["Content-Type", "Authorization"])

# Inicializar MongoDB
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
    uploads_dir = os.path.join(os.getcwd(), 'uploads')
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir, exist_ok=True)
    return send_from_directory(uploads_dir, filename)

# --- Importar y registrar Blueprints ---
try:
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
except Exception as e:
    print("❌ Error al cargar blueprints:", e)
    raise

# --- Ruta raíz ---
@app.route("/")
def home():
    return "API Quickflow funcionando ✅"

# --- Manejo de errores generales ---
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Ruta no encontrada"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Error interno del servidor"}), 500

# --- Ejecutar ---
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)  # ✅ debug=False en producción
