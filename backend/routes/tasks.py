from flask import Blueprint, request, jsonify, current_app, send_from_directory
from bson.objectid import ObjectId
from datetime import datetime
from backend.auth_utils import token_required
import os

tasks_bp = Blueprint("tasks", __name__)

def get_db():
    return current_app.mongo.db.tareas

@tasks_bp.route("/tasks", methods=["POST"])
@token_required
def crear_tarea():
    data = request.form
    titulo = data.get("titulo")
    descripcion = data.get("descripcion", "")
    estado = data.get("estado", "pendiente")
    fecha = data.get("fecha", datetime.utcnow().strftime("%Y-%m-%d"))
    hora = data.get("hora", "")
    categoria = data.get("categoria", "")
    nota = data.get("nota", "")
    enlace = data.get("enlace", "")
    subtareas = data.get("subtareas", "[]")

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
        "hora": hora,
        "categoria": categoria,
        "nota": nota,
        "enlace": enlace,
        "subtareas": eval(subtareas),
        "usuario": request.user_email
    }

    # archivo adjunto
    if 'archivo' in request.files:
        archivo = request.files['archivo']
        if archivo.filename:
            nombre_archivo = archivo.filename
            uploads_dir = os.path.join(os.getcwd(), 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            archivo_path = os.path.join(uploads_dir, nombre_archivo)
            archivo.save(archivo_path)
            tarea["archivo"] = f"uploads/{nombre_archivo}"

    db = get_db()
    result = db.insert_one(tarea)
    tarea["_id"] = str(result.inserted_id)

    # ✅ incluir archivoUrl en la respuesta si aplica
    if "archivo" in tarea:
        tarea["archivoUrl"] = f"{request.host_url.rstrip('/')}/{tarea['archivo']}"

    return jsonify(tarea), 201

@tasks_bp.route("/tasks/<id>", methods=["PUT"])
@token_required
def actualizar_tarea(id):
    data = request.get_json()
    db = get_db()

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

@tasks_bp.route("/tasks", methods=["GET"])
@token_required
def obtener_tareas():
    db = get_db()
    tareas = list(db.find({"usuario": request.user_email}))
    for tarea in tareas:
        tarea["_id"] = str(tarea["_id"])
        if "archivo" in tarea:
            tarea["archivoUrl"] = f"{request.host_url.rstrip('/')}/{tarea['archivo']}"
    return jsonify(tareas)

@tasks_bp.route("/tasks/<id>", methods=["DELETE"])
@token_required
def eliminar_tarea(id):
    db = get_db()
    result = db.delete_one({"_id": ObjectId(id), "usuario": request.user_email})
    if result.deleted_count == 0:
        return jsonify({"error": "Tarea no encontrada o no autorizada"}), 404
    return jsonify({"message": "Tarea eliminada"}), 200


