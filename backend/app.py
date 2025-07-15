from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
import os

mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Cargar variables locales si no estamos en Render
    if os.environ.get("RENDER") != "true":
        from dotenv import load_dotenv
        load_dotenv()

    MONGO_URI = os.getenv("MONGO_URI")
    if not MONGO_URI:
        print("❌ MONGO_URI no está definido")
    else:
        app.config["MONGO_URI"] = MONGO_URI
        mongo.init_app(app)
        try:
            with app.app_context():
                mongo.cx.server_info()
                print("✅ Conectado exitosamente a MongoDB Atlas")
        except Exception as e:
            print(f"❌ Error al conectar a MongoDB Atlas: {e}")

    # === Rutas ===
    @app.route("/", methods=["GET"])
    def home():
        return jsonify({"message": "Quickflow API funcionando correctamente"}), 200

    @app.route("/api/register", methods=["POST"])
    def register():
        print("👉 Ingresando a /api/register")
        try:
            if not mongo or not mongo.db:
                print("❌ Mongo no está conectado")
                return jsonify({"error": "Error de conexión con la base de datos"}), 500

            data = request.json
            print(f"📥 Datos recibidos: {data}")

            email = data.get("email")
            password = data.get("password")
            username = data.get("username") or email

            if not email or not password:
                print("⚠️ Datos incompletos")
                return jsonify({"error": "Datos incompletos"}), 400

            users = mongo.db.users

            if users.find_one({"email": email}):
                print("⚠️ El correo ya está registrado")
                return jsonify({"error": "El correo ya está registrado"}), 409

            users.insert_one({
                "username": username,
                "email": email,
                "password": password  # ⚠️ pendiente cifrado
            })

            print("✅ Usuario registrado con éxito")
            return jsonify({"message": "Usuario registrado correctamente"}), 201

        except Exception as e:
            print(f"❌ Error interno en /api/register: {e}")
            return jsonify({"error": "Error interno en el servidor", "details": str(e)}), 500

    @app.route("/api/login", methods=["POST"])
    def login():
        try:
            if not mongo or not mongo.db:
                print("❌ Mongo no está conectado")
                return jsonify({"error": "Error de conexión con la base de datos"}), 500

            data = request.json
            email = data.get("email")
            password = data.get("password")

            if not email or not password:
                return jsonify({"error": "Datos incompletos"}), 400

            users = mongo.db.users
            user = users.find_one({"email": email})

            if not user:
                return jsonify({"error": "Usuario no encontrado"}), 404

            if user["password"] != password:
                return jsonify({"error": "Contraseña incorrecta"}), 401

            token = "fake-jwt-token"
            return jsonify({"message": "Inicio de sesión exitoso", "token": token}), 200

        except Exception as e:
            print(f"❌ Error interno en /api/login: {e}")
            return jsonify({"error": "Error interno en el servidor", "details": str(e)}), 500

    return app

# Gunicorn usa esto
app = create_app()

# Solo para desarrollo local
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
