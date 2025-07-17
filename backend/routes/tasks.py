from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
from bson.objectid import ObjectId
from datetime import datetime
from backend.auth_utils import token_required  # 👈 Importa el decorador

tasks_bp = Blueprint("tasks", __name__)

# --- BASE DE DATOS ---
def get_db():
    return current_app.mongo.db.tareas

# --- CREAR TAREA ---
@tasks_bp.route("/", methods=["POST", "OPTIONS"])
@cross_origin(origins="https://peppy-starlight-fd4c37.netlify.app", supports_credentials=True)
@token_required
def crear_tarea():
    if request.method == "OPTIONS":
        return '', 200

    data = request.get_json()
    tarea = {
        "titulo": data.get("titulo"),
        "descripcion": data.get("descripcion"),
        "estado": data.get("estado", "pendiente"),
        "fecha": data.get("fecha", datetime.utcnow().strftime("%Y-%m-%d")),
        "usuario": request.user_email
    }
    db = get_db()
    result = db.insert_one(tarea)
    tarea["_id"] = str(result.inserted_id)
    return jsonify(tarea), 201

# --- OBTENER TAREAS ---
@tasks_bp.route("/", methods=["GET", "OPTIONS"])
@cross_origin(origins="https://peppy-starlight-fd4c37.netlify.app", supports_credentials=True)
@token_required
def obtener_tareas():
    if request.method == "OPTIONS":
        return '', 200

    db = get_db()
    tareas = list(db.find({"usuario": request.user_email}))
    for t in tareas:
        t["_id"] = str(t["_id"])
    return jsonify(tareas)

# --- ACTUALIZAR TAREA ---
@tasks_bp.route("/<id>", methods=["PUT", "OPTIONS"])
@cross_origin(origins="https://peppy-starlight-fd4c37.netlify.app", supports_credentials=True)
@token_required
def actualizar_tarea(id):
    if request.method == "OPTIONS":
        return '', 200

    data = request.get_json()
    db = get_db()
    db.update_one({"_id": ObjectId(id), "usuario": request.user_email}, {"$set": data})
    return jsonify({"message": "Tarea actualizada"}), 200

# --- ELIMINAR TAREA ---
@tasks_bp.route("/<id>", methods=["DELETE", "OPTIONS"])
@cross_origin(origins="https://peppy-starlight-fd4c37.netlify.app", supports_credentials=True)
@token_required
def eliminar_tarea(id):
    if request.method == "OPTIONS":
        return '', 200

    db = get_db()
    db.delete_one({"_id": ObjectId(id), "usuario": request.user_email})
    return jsonify({"message": "Tarea eliminada"}), 200
