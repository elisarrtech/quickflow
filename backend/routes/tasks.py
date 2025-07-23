from flask import Blueprint, request, jsonify, current_app
from bson.objectid import ObjectId
from datetime import datetime
from backend.auth_utils import token_required

tasks_bp = Blueprint("tasks", __name__)

def get_db():
    return current_app.mongo.db.tareas

# ✅ Crear tarea (solo si el token es válido)
@tasks_bp.route("/tasks", methods=["POST"])  # ⬅️ ajustado
@token_required
def crear_tarea():
    data = request.get_json()
    tarea = {
        "titulo": data.get("titulo"),
        "descripcion": data.get("descripcion"),
        "estado": data.get("estado", "pendiente"),
        "fecha": data.get("fecha", datetime.utcnow().strftime("%Y-%m-%d")),
        "usuario": request.user_email  # viene del token
    }

    db = get_db()
    result = db.insert_one(tarea)
    tarea["_id"] = str(result.inserted_id)

    return jsonify(tarea), 201

# ✅ Obtener tareas del usuario autenticado
@tasks_bp.route("/tasks", methods=["GET"])  # ⬅️ ajustado
@token_required
def obtener_tareas():
    db = get_db()
    tareas = list(db.find({"usuario": request.user_email}))

    for tarea in tareas:
        tarea["_id"] = str(tarea["_id"])

    return jsonify(tareas)

# ✅ Actualizar tarea (solo si pertenece al usuario)
@tasks_bp.route("/tasks/<id>", methods=["PUT"])  # ⬅️ ajustado
@token_required
def actualizar_tarea(id):
    data = request.get_json()
    db = get_db()

    result = db.update_one(
        {"_id": ObjectId(id), "usuario": request.user_email},
        {"$set": data}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Tarea no encontrada o no autorizada"}), 404

    return jsonify({"message": "Tarea actualizada"}), 200

# ✅ Eliminar tarea (solo si pertenece al usuario)
@tasks_bp.route("/tasks/<id>", methods=["DELETE"])  # ⬅️ ajustado
@token_required
def eliminar_tarea(id):
    db = get_db()

    result = db.delete_one({"_id": ObjectId(id), "usuario": request.user_email})

    if result.deleted_count == 0:
        return jsonify({"error": "Tarea no encontrada o no autorizada"}), 404

    return jsonify({"message": "Tarea eliminada"}), 200
