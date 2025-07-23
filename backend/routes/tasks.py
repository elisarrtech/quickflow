from flask import Blueprint, request, jsonify, current_app
from bson.objectid import ObjectId
from datetime import datetime
from backend.auth_utils import token_required

tasks_bp = Blueprint("tasks", __name__)

def get_db():
    return current_app.mongo.db.tareas

# ✅ Crear tarea (con validaciones + categoría)
@tasks_bp.route("/tasks", methods=["POST"])
@token_required
def crear_tarea():
    data = request.get_json()
    titulo = data.get("titulo")
    descripcion = data.get("descripcion", "")
    estado = data.get("estado", "pendiente")
    fecha = data.get("fecha", datetime.utcnow().strftime("%Y-%m-%d"))
    categoria = data.get("categoria", "")  # <-- nuevo campo opcional

    # Validaciones
    if not titulo:
        return jsonify({"error": "El título es obligatorio."}), 400
    if estado not in ["pendiente", "completada"]:
        return jsonify({"error": "Estado no válido."}), 400
    try:
        datetime.strptime(fecha, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Formato de fecha inválido. Usa YYYY-MM-DD."}), 400

    tarea = {
        "titulo": titulo,
        "descripcion": descripcion,
        "estado": estado,
        "fecha": fecha,
        "categoria": categoria,  # <-- guardar categoría
        "usuario": request.user_email
    }

    db = get_db()
    result = db.insert_one(tarea)
    tarea["_id"] = str(result.inserted_id)

    return jsonify(tarea), 201

# ✅ Obtener tareas del usuario autenticado
@tasks_bp.route("/tasks", methods=["GET"])
@token_required
def obtener_tareas():
    db = get_db()
    tareas = list(db.find({"usuario": request.user_email}))

    for tarea in tareas:
        tarea["_id"] = str(tarea["_id"])

    return jsonify(tareas)

# ✅ Actualizar tarea (con validaciones + soporte para categoría)
@tasks_bp.route("/tasks/<id>", methods=["PUT"])
@token_required
def actualizar_tarea(id):
    data = request.get_json()
    db = get_db()

    # Validaciones (solo si los campos existen)
    if "titulo" in data and not data["titulo"]:
        return jsonify({"error": "El título no puede estar vacío."}), 400
    if "estado" in data and data["estado"] not in ["pendiente", "completada"]:
        return jsonify({"error": "Estado no válido."}), 400
    if "fecha" in data:
        try:
            datetime.strptime(data["fecha"], "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido. Usa YYYY-MM-DD."}), 400

    result = db.update_one(
        {"_id": ObjectId(id), "usuario": request.user_email},
        {"$set": data}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Tarea no encontrada o no autorizada"}), 404

    return jsonify({"message": "Tarea actualizada"}), 200

# ✅ Eliminar tarea
@tasks_bp.route("/tasks/<id>", methods=["DELETE"])
@token_required
def eliminar_tarea(id):
    db = get_db()

    result = db.delete_one({"_id": ObjectId(id), "usuario": request.user_email})

    if result.deleted_count == 0:
        return jsonify({"error": "Tarea no encontrada o no autorizada"}), 404

    return jsonify({"message": "Tarea eliminada"}), 200
