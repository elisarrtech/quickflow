from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from flask_pymongo import PyMongo
from datetime import datetime

tasks_bp = Blueprint("tasks", __name__)

def get_db():
    from app import mongo
    return mongo.db.tareas

# Crear una tarea
@tasks_bp.route("/api/tasks", methods=["POST"])
def crear_tarea():
    data = request.get_json()
    tarea = {
        "titulo": data.get("titulo"),
        "descripcion": data.get("descripcion"),
        "estado": data.get("estado", "pendiente"),
        "fecha": data.get("fecha", datetime.utcnow().strftime("%Y-%m-%d")),
        "usuario": data.get("usuario", None)
    }
    db = get_db()
    result = db.insert_one(tarea)
    tarea["_id"] = str(result.inserted_id)
    return jsonify(tarea), 201

# Obtener todas las tareas
@tasks_bp.route("/api/tasks", methods=["GET"])
def obtener_tareas():
    db = get_db()
    tareas = list(db.find())
    for t in tareas:
        t["_id"] = str(t["_id"])
    return jsonify(tareas)

# Actualizar tarea por ID
@tasks_bp.route("/api/tasks/<id>", methods=["PUT"])
def actualizar_tarea(id):
    data = request.get_json()
    db = get_db()
    db.update_one({"_id": ObjectId(id)}, {"$set": data})
    return jsonify({"message": "Tarea actualizada"}), 200

# Eliminar tarea por ID
@tasks_bp.route("/api/tasks/<id>", methods=["DELETE"])
def eliminar_tarea(id):
    db = get_db()
    db.delete_one({"_id": ObjectId(id)})
    return jsonify({"message": "Tarea eliminada"}), 200
