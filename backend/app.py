from flask import Flask
from flask_cors import CORS
import os

app = Flask(__name__)  # ✅ Primero creamos la instancia de Flask

# ✅ Luego configuramos CORS
CORS(app,
     origins=["https://peppy-starlight-fd4c37.netlify.app"],
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

# ✅ Registrar alertas después de crear app
app.register_blueprint(alertas_bp)

# ✅ Ruta para servir archivos subidos
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(os.path.join(os.getcwd(), 'uploads'), filename)

# --- Configuración CORS ---
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

# --- Verificar conexión a MongoDB ---
try:
    mongo.cx.server_info()
    print("✅ Conectado a MongoDB Atlas")
except Exception as e:
    print("❌ Error al conectar a MongoDB:", e)

# --- Importar y registrar otros Blueprints ---
from backend.routes.auth import auth_bp
from backend.routes.tasks import tasks_bp
from backend.routes.perfil import perfil_bp
from backend.routes.eventos_routes import eventos_bp

app.register_blueprint(eventos_bp)
app.register_blueprint(auth_bp, url_prefix="/api")
app.register_blueprint(tasks_bp, url_prefix="/api")
app.register_blueprint(perfil_bp, url_prefix="/api")

# --- Ruta de prueba ---
@app.route("/")
def home():
    return "API Quickflow funcionando ✅"

# --- Ejecución local ---
if __name__ == "__main__":
    app.run(debug=True, port=5000)
