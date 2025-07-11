from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
import os

# 📦 Importa las funciones de autenticación
from backend.auth import hash_password, check_password, generate_token

app = Flask(__name__)
CORS(app)

# 🔑 Configuración de MongoDB Atlas (directa por ahora)
app.config["MONGO_URI"] = "mongodb+srv://misselisavirtual:Test1234@cluster0.sv2xrde.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"


# 🔑 Llave secreta para JWT
app.config['SECRET_KEY'] = 'tu-clave-secreta-aqui'  # Reemplaza esto por una clave segura

# 🔌 Conexión MongoDB
mongo = PyMongo(app)

# ✔ Verifica conexión
try:
    mongo.cx.server_info()
    print("✅ Conectado exitosamente a MongoDB Atlas")
except Exception as e:
    print("❌ Error al conectar a MongoDB Atlas:", e)

# ✔ Ruta de prueba
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Quickflow API funcionando correctamente"}), 200

# ✔ Registro de usuarios con contraseña cifrada
@app.route("/api/register", methods=["POST"])
def register():
    data = request.json

    if not data or not data.get("username") or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Datos incompletos"}), 400

    users = mongo.db.users

    if users.find_one({"email": data.get("email")}):
        return jsonify({"error": "El correo ya está registrado"}), 409

    hashed_pw = hash_password(data.get("password"))

    users.insert_one({
        "username": data.get("username"),
        "email": data.get("email"),
        "password": hashed_pw
    })

    return jsonify({"message": "Usuario registrado correctamente"}), 201

# ✔ Login con validación y token JWT
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Datos incompletos"}), 400

    users = mongo.db.users
    user = users.find_one({"email": email})

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    if not check_password(user["password"], password):
        return jsonify({"error": "Contraseña incorrecta"}), 401

    token = generate_token(str(user["_id"]))

    return jsonify({"message": "Inicio de sesión exitoso", "token": token}), 200

# ✔ Iniciar app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
