from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
import os

# ✅ Solo carga dotenv localmente
if os.environ.get("RENDER") != "true":
    from dotenv import load_dotenv
    load_dotenv()

app = Flask(__name__)
CORS(app)

# 🔑 URI desde variables de entorno
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

# 🔌 Inicializar conexión MongoDB
mongo = PyMongo()
mongo.init_app(app)

# ✔ Ruta de prueba
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Quickflow API funcionando correctamente"}), 200

# ✔ Registro de usuarios
@app.route("/api/register", methods=["POST"])
def register():
    print("👉 Ingresando a /api/register")

    try:
        data = request.json
        print(f"📥 Datos recibidos: {data}")

        if not data or not data.get("username") or not data.get("email") or not data.get("password"):
            print("⚠️ Datos incompletos")
            return jsonify({"error": "Datos incompletos"}), 400

        users = mongo.db.users

        if users.find_one({"email": data.get("email")}):
            print("⚠️ El correo ya existe")
            return jsonify({"error": "El correo ya está registrado"}), 409

        users.insert_one({
            "username": data.get("username"),
            "email": data.get("email"),
            "password": data.get("password")  # ⚠️ Solo para pruebas, falta hash
        })

        print("✅ Usuario registrado con éxito")
        return jsonify({"message": "Usuario registrado correctamente"}), 201

    except Exception as e:
        print(f"❌ Error interno en /api/register: {e}")
        return jsonify({"error": "Error interno en el servidor", "details": str(e)}), 500

# ✔ Login de usuarios
@app.route("/api/login", methods=["POST"])
def login():
    print("👉 Ingresando a /api/login")

    try:
        data = request.json
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            print("⚠️ Datos incompletos")
            return jsonify({"error": "Datos incompletos"}), 400

        users = mongo.db.users
        user = users.find_one({"email": email})

        if not user:
            print("⚠️ Usuario no encontrado")
            return jsonify({"error": "Usuario no encontrado"}), 404

        if user.get("password") != password:
            print("⚠️ Contraseña incorrecta")
            return jsonify({"error": "Contraseña incorrecta"}), 401

        token = "fake-jwt-token"

        print("✅ Inicio de sesión exitoso")
        return jsonify({"message": "Inicio de sesión exitoso", "token": token}), 200

    except Exception as e:
        print(f"❌ Error interno en /api/login: {e}")
        return jsonify({"error": "Error interno en el servidor", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
