from flask import Blueprint, request, jsonify, current_app
from bson.objectid import ObjectId
from datetime import datetime
from backend.auth_utils import token_required  # 👈 Importa el decorador

tasks_bp = Blueprint("tasks", __name__)

def get_db():
    return current_app.mongo.db.tareas

@tasks_bp.route("/", methods=["POST"])
@token_required
def crear_tarea():
    data = request.get_json()
    tarea = {
        "titulo": data.get("titulo"),
        "descripcion": data.get("descripcion"),
        "estado": data.get("estado", "pendiente"),
        "fecha": data.get("fecha", datetime.utcnow().strftime("%Y-%m-%d")),
        "usuario": request.user_email  # 👈 obtenido del token
    }
    db = get_db()
    result = db.insert_one(tarea)
    tarea["_id"] = str(result.inserted_id)
    return jsonify(tarea), 201

@tasks_bp.route("/", methods=["GET"])
@token_required
def obtener_tareas():
    db = get_db()
    tareas = list(db.find({"usuario": request.user_email}))  # 👈 Solo sus tareas
    for t in tareas:
        t["_id"] = str(t["_id"])
    return jsonify(tareas)

@tasks_bp.route("/<id>", methods=["PUT"])
@token_required
def actualizar_tarea(id):
    data = request.get_json()
    db = get_db()
    db.update_one({"_id": ObjectId(id), "usuario": request.user_email}, {"$set": data})
    return jsonify({"message": "Tarea actualizada"}), 200

@tasks_bp.route("/<id>", methods=["DELETE"])
@token_required
def eliminar_tarea(id):
    db = get_db()
    db.delete_one({"_id": ObjectId(id), "usuario": request.user_email})
    return jsonify({"message": "Tarea eliminada"}), 200
