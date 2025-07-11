from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 🔑 Conexión a MongoDB Atlas (reemplaza la contraseña por la correcta)
app.config["MONGO_URI"] = "mongodb+srv://misselisavirtual:Test1234!@cluster0.sv2xrde.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# 🔌 Inicializar Mongo
mongo = PyMongo(app)

# ✔ Verificar conexión
try:
    mongo.cx.server_info()
    print("✅ Conectado exitosamente a MongoDB Atlas")
except Exception as e:
    print("❌ Error al conectar a MongoDB Atlas:", e)

# ✔ Ruta raíz
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Quickflow API funcionando correctamente"}), 200

# ✔ Registro
@app.route("/api/register", methods=["POST"])
def register():
    data = request.json

    if not data or not data.get("username") or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Datos incompletos"}), 400

    users = mongo.db.users

    if users.find_one({"email": data.get("email")}):
        return jsonify({"error": "El correo ya está registrado"}), 409

    users.insert_one({
        "username": data.get("username"),
        "email": data.get("email"),
        "password": data.get("password")  # ⚠️ Pendiente cifrado
    })

    return jsonify({"message": "Usuario registrado correctamente"}), 201

# ✔ Login
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

    if user["password"] != password:
        return jsonify({"error": "Contraseña incorrecta"}), 401

    return jsonify({"message": "Inicio de sesión exitoso", "token": "fake-jwt-token"}), 200

# ✔ Iniciar la app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
