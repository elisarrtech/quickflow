from flask import Flask, request, send_from_directory
from flask_cors import CORS
from flask_pymongo import PyMongo
import os

# --- Inicializar Flask ---
app = Flask(__name__)

# --- Configuración CORS (sin espacios extra, y bien definido) ---
CORS(app,
     origins=["https://peppy-starlight-fd4c37.netlify.app"],  # ✅ sin espacios
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

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
    print(f"👉 Headers: {dict(request.headers)}")

# --- Elimina el after_request si usas flask-cors correctamente ---
# No es necesario duplicar las cabeceras CORS si ya usas flask-cors
# Comenta o elimina esta función:
# @app.after_request
# def after_request(response):
#     response.headers.add("Access-Control-Allow-Origin", "https://peppy-starlight-fd4c37.netlify.app  ")
#     response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
#     response.headers.add("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
#     return response

# --- Manejador de OPTIONS si es necesario ---
@app.route('/api/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    response = app.make_response('')
    response.headers["Access-Control-Allow-Origin"] = "https://peppy-starlight-fd4c37.netlify.app"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    return response, 204

# --- Ruta para servir archivos subidos ---
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(os.path.join(os.getcwd(), 'uploads'), filename)

# --- Importar y registrar Blueprints ---
from backend.routes.auth import auth_bp
from backend.routes.tasks import tasks_bp
from backend.routes.perfil import perfil_bp
from backend.routes.eventos_routes import eventos_bp
from backend.routes.alerts_routes import alerts_bp  # ✅ NUEVO

app.register_blueprint(auth_bp, url_prefix="/api")
app.register_blueprint(tasks_bp, url_prefix="/api")
app.register_blueprint(perfil_bp, url_prefix="/api")
app.register_blueprint(eventos_bp, url_prefix="/api")
app.register_blueprint(alerts_bp, url_prefix="/api")  # ✅ NUEVO

# --- Ruta raíz de prueba ---
@app.route("/")
def home():
    return "API Quickflow funcionando ✅"

# --- Ejecutar localmente ---
if __name__ == "__main__":
    app.run(debug=True, port=5000)
