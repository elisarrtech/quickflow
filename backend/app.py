from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
import os

# Extensión global de PyMongo (sin app)
mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Cargar .env si no es entorno Render
    if os.environ.get("RENDER") != "true":
        from dotenv import load_dotenv
        load_dotenv()

    # Configuración de Mongo
    MONGO_URI = os.getenv("MONGO_URI")
    if not MONGO_URI:
        print("❌ MONGO_URI no está definido")
    else:
        app.config["MONGO_URI"] = MONGO_URI
        mongo.init_app(app)

        # Validar conexión solo en contexto
        try:
            with app.app_context():
                mongo.cx.server_info()
                print("✅ Conectado exitosamente a MongoDB Atlas")
        except Exception as e:
            print(f"❌ Error al conectar a MongoDB Atlas: {e}")

    # === RUTAS ===
    @app.route("/", methods=["GET"])
    def home():
        return jsonify({"message": "Quickflow API funcionando correctamente"}), 200

    @app.route("/api/register", methods=["POST"])
    def register():
        print("👉 Ingresando a /api/register")
        try:
            db = mongo.db
        except Exception as e:
            print("❌ Mongo no está conectado")
            return jsonify({"error": "Error de conexión con MongoDB"}), 500

        data = request.json
        print(f"📥 Datos recibidos: {data}")

        email = data.get("email")
        password = data.get("password")
        username = data.get("username") or email

        if not email or not password:
            return jsonify({"error": "Datos incompletos"}), 400

        if db.users.find_one({"email": email}):
            return jsonify({"error": "El correo ya está registrado"}), 409

        db.users.insert_one({
            "username": username,
            "email": email,
            "password": password
        })

        return jsonify({"message": "Usuario registrado correctamente"}), 201

    @app.route("/api/login", methods=["POST"])
    def login():
        try:
            db = mongo.db
        except Exception as e:
            print("❌ Mongo no está conectado")
            return jsonify({"error": "Error de conexión con MongoDB"}), 500

        data = request.json
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Datos incompletos"}), 400

        user = db.users.find_one({"email": email})

        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        if user["password"] != password:
            return jsonify({"error": "Contraseña incorrecta"}), 401

        return jsonify({"message": "Inicio de sesión exitoso", "token": "fake-jwt-token"}), 200

    return app

# Inicialización con Gunicorn
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
