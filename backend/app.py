from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from dotenv import load_dotenv
import os

# ✅ Cargar variables de entorno desde .env (solo localmente)
load_dotenv()

app = Flask(__name__)
CORS(app)

# ✅ Leer la URI desde la variable de entorno
app.config["MONGO_URI"] = os.getenv("MONGO_URI")

# 🔌 Conexión MongoDB
mongo = PyMongo(app)

# ✔ Verificar conexión inicial
try:
    mongo.cx.server_info()
    print("✅ Conectado exitosamente a MongoDB Atlas")
except Exception as e:
    print(f"❌ Error al conectar a MongoDB Atlas: {e}")
    mongo = None  # Evita que el objeto cause errores más adelante


# ✔ Ruta de prueba
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Quickflow API funcionando correctamente"}), 200


# ✔ Registro de usuarios
@app.route("/api/register", methods=["POST"])
def register():
    if mongo is None:
        return jsonify({"error": "Error de conexión con la base de datos"}), 500

    data = request.json

    if not data or not data.get("username") or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Datos incompletos"}), 400

    users = mongo.db.users

    # Verificar si el usuario ya existe
    if users.find_one({"email": data.get("email")}):
        return jsonify({"error": "El correo ya está registrado"}), 409

    users.insert_one({
        "username": data.get("username"),
        "email": data.get("email"),
        "password": data.get("password")  # ⚠️ Recuerda cifrar la contraseña en producción
    })

    return jsonify({"message": "Usuario registrado correctamente"}), 201


# ✔ Login de usuarios
@app.route("/api/login", methods=["POST"])
def login():
    if mongo is None:
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

    # ⚠️ Contraseña sin cifrado (sólo pruebas iniciales)
    if user["password"] != password:
        return jsonify({"error": "Contraseña incorrecta"}), 401

    # Simulamos un token
    token = "fake-jwt-token"

    return jsonify({"message": "Inicio de sesión exitoso", "token": token}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
