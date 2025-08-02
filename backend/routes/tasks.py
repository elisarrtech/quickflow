# backend/routes/tasks.py
from flask import Blueprint, request, jsonify, current_app
from bson.objectid import ObjectId
from datetime import datetime
from backend.auth_utils import token_required
from flask_cors import cross_origin
import os
import json

tasks_bp = Blueprint("tasks", __name__)

def get_db():
    return current_app.mongo.db.tareas

def usuario_existe(email):
    """Verifica si un usuario existe en la base de datos."""
    return current_app.mongo.db.users.find_one({"email": email}) is not None

@tasks_bp.route("/tasks", methods=["POST"])
@token_required
@cross_origin(origins=["https://peppy-starlight-fd4c37.netlify.app"], supports_credentials=True)
def crear_tarea(usuario_email):
    data = request.form
    titulo = data.get("titulo")
    descripcion = data.get("descripcion", "")
    estado = data.get("estado", "pendiente")
    fecha = data.get("fecha", datetime.utcnow().strftime("%Y-%m-%d"))
    hora = data.get("hora", "")
    categoria = data.get("categoria", "")
    nota = data.get("nota", "")
    enlace = data.get("enlace", "")
    asignadoA = data.get("asignadoA", "")
    subtareas_raw = data.get("subtareas", "[]")
    prioridad = data.get("prioridad", "media")
    compartido_con_raw = data.get("compartido_con", "[]")

    # Validar subtareas
    try:
        subtareas = json.loads(subtareas_raw)
    except json.JSONDecodeError:
        subtareas = []

    # Validar usuarios compartidos
    try:
        compartido_con = json.loads(compartido_con_raw)
        if not isinstance(compartido_con, list):
            compartido_con = []
    except json.JSONDecodeError:
        compartido_con = []

    # Validar que los usuarios existan
    if asignadoA and not usuario_existe(asignadoA):
        return jsonify({"error": f"El usuario asignado '{asignadoA}' no existe"}), 400

    for email in compartido_con:
        if not usuario_existe(email):
            return jsonify({"error": f"El usuario '{email}' en 'compartido_con' no existe"}), 400

    if not titulo:
        return jsonify({"error": "El título es obligatorio."}), 400
    if estado not in ["pendiente", "completada"]:
        return jsonify({"error": "Estado no válido."}), 400
    try:
        datetime.strptime(fecha, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Formato de fecha inválido. Usa YYYY-MM-DD."}), 400
    if prioridad not in ["alta", "media", "baja"]:
        return jsonify({"error": "Prioridad no válida."}), 400

    tarea = {
        "titulo": titulo,
        "descripcion": descripcion,
        "estado": estado,
        "fecha": fecha,
        "hora": hora,
        "categoria": categoria,
        "nota": nota,
        "enlace": enlace,
        "asignadoA": asignadoA,
        "subtareas": subtareas,
        "usuario": usuario_email,
        "prioridad": prioridad,
        "compartido_con": compartido_con,
        "comentarios": [],
        "historial": [{"accion": "Tarea creada", "fecha": datetime.utcnow().isoformat()}]
    }

    # Guardar archivo si viene
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

    if "archivo" in tarea:
        tarea["archivoUrl"] = f"{request.host_url.rstrip('/')}/{tarea['archivo']}"

    return jsonify(tarea), 201


@tasks_bp.route("/tasks/<id>", methods=["PUT"])
@token_required
def actualizar_tarea(usuario_email, id):
    data = request.get_json()
    db = get_db()

    if not data:
        return jsonify({"error": "No se enviaron datos."}), 400

    # Validaciones
    if "titulo" in data and not data["titulo"].strip():
        return jsonify({"error": "El título no puede estar vacío."}), 400

    if "estado" in data and data["estado"] not in ["pendiente", "completada"]:
        return jsonify({"error": "Estado no válido."}), 400

    if "fecha" in data:
        try:
            datetime.strptime(data["fecha"], "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido. Usa YYYY-MM-DD."}), 400

    if "prioridad" in data and data["prioridad"] not in ["alta", "media", "baja"]:
        return jsonify({"error": "Prioridad no válida."}), 400

    # Buscar tarea
    tarea = db.find_one({"_id": ObjectId(id)})
    if not tarea:
        return jsonify({"error": "Tarea no encontrada"}), 404

    # Verificar que el usuario tiene permiso para editar
    if tarea["usuario"] != usuario_email and \
       tarea.get("asignadoA") != usuario_email and \
       usuario_email not in tarea.get("compartido_con", []):
        return jsonify({"error": "No autorizado para editar esta tarea"}), 403

    # Preparar actualización
    update_data = {"$set": {}}
    historial_acciones = []

    campos_a_actualizar = [
        "titulo", "descripcion", "estado", "fecha", "hora",
        "categoria", "nota", "enlace", "asignadoA", "subtareas", "prioridad"
    ]
    for campo in campos_a_actualizar:
        if campo in data:
            valor_nuevo = data[campo]
            valor_viejo = tarea.get(campo)
            if valor_nuevo != valor_viejo:
                update_data["$set"][campo] = valor_nuevo

                # Registrar en historial
                if campo == "estado":
                    historial_acciones.append(f"Tarea marcada como {valor_nuevo}")
                elif campo == "prioridad":
                    historial_acciones.append(f"Prioridad cambiada a {valor_nuevo}")
                elif campo == "asignadoA":
                    historial_acciones.append(f"Tarea asignada a {valor_nuevo}")
                elif campo == "subtareas":
                    viejas = {s.get("texto"): s.get("completada", False) for s in valor_viejo if isinstance(s, dict)}
                    for sub in valor_nuevo:
                        if isinstance(sub, dict) and sub.get("completada", False):
                            texto = sub["texto"]
                            if not viejas.get(texto, False):
                                historial_acciones.append(f"Subtarea '{texto}' completada")
                else:
                    historial_acciones.append(f"{campo.capitalize()} actualizado")

    # Manejar 'compartido_con'
    if "compartido_con" in data:
        nuevos_emails = data["compartido_con"]
        if not isinstance(nuevos_emails, list):
            return jsonify({"error": "'compartido_con' debe ser una lista de emails"}), 400

        # Validar que los usuarios existan
        for email in nuevos_emails:
            if not usuario_existe(email):
                return jsonify({"error": f"El usuario '{email}' no existe"}), 400

        viejos_emails = set(tarea.get("compartido_con", []))
        nuevos_emails_set = set(nuevos_emails)
        agregados = nuevos_emails_set - viejos_emails
        eliminados = viejos_emails - nuevos_emails_set

        if agregados:
            historial_acciones.append(f"Tarea compartida con: {', '.join(agregados)}")
        if eliminados:
            historial_acciones.append(f"Acceso revocado a: {', '.join(eliminados)}")

        update_data["$set"]["compartido_con"] = nuevos_emails

    # Añadir historial si hay cambios
    if historial_acciones:
        now = datetime.utcnow().isoformat()
        historial_updates = [{"accion": accion, "fecha": now} for accion in historial_acciones]
        update_data.setdefault("$push", {})["historial"] = {"$each": historial_updates}

    # Si no hay cambios, no hacer nada
    if len(update_data["$set"]) == 0:
        # Devolver tarea actualizada
        tarea_actualizada = db.find_one({"_id": ObjectId(id)})
        return jsonify(formatear_tarea(tarea_actualizada)), 200

    # Ejecutar actualización
    result = db.update_one(
        {"_id": ObjectId(id)},
        update_data
    )

    if result.matched_count == 0:
        return jsonify({"error": "Tarea no encontrada"}), 404

    # Devolver tarea actualizada
    tarea_actualizada = db.find_one({"_id": ObjectId(id)})
    return jsonify(formatear_tarea(tarea_actualizada)), 200


@tasks_bp.route("/tasks", methods=["GET"])
@token_required
def obtener_tareas(usuario_email):
    db = get_db()
    # Obtener tareas donde el usuario es dueño, está asignado o compartido
    tareas = list(db.find({
        "$or": [
            {"usuario": usuario_email},
            {"asignadoA": usuario_email},
            {"compartido_con": usuario_email}
        ]
    }))
    tareas_formateadas = [formatear_tarea(t) for t in tareas]
    return jsonify(tareas_formateadas)


@tasks_bp.route("/tasks/<id>", methods=["DELETE"])
@token_required
def eliminar_tarea(usuario_email, id):
    db = get_db()
    tarea = db.find_one({"_id": ObjectId(id)})
    if not tarea:
        return jsonify({"error": "Tarea no encontrada"}), 404

    # Solo el dueño puede eliminar
    if tarea["usuario"] != usuario_email:
        return jsonify({"error": "No autorizado para eliminar esta tarea"}), 403

    result = db.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Tarea no encontrada"}), 404
    return jsonify({"message": "Tarea eliminada"}), 200


@tasks_bp.route("/tasks/<id>/comentarios", methods=["POST"])
@token_required
def agregar_comentario(usuario_email, id):
    db = get_db()
    tarea = db.find_one({"_id": ObjectId(id)})
    if not tarea:
        return jsonify({"error": "Tarea no encontrada"}), 404

    # Verificar permisos
    if (tarea["usuario"] != usuario_email and
        tarea.get("asignadoA") != usuario_email and
        usuario_email not in tarea.get("compartido_con", [])):
        return jsonify({"error": "No autorizado para comentar"}), 403

    data = request.get_json()
    texto = data.get("texto", "").strip()

    if not texto:
        return jsonify({"error": "El comentario no puede estar vacío"}), 400

    comentario = {
        "texto": texto,
        "autor": usuario_email,
        "fecha": datetime.utcnow().isoformat()
    }

    accion_historial = f"Comentó: {texto[:50]}{'...' if len(texto) > 50 else ''}"

    db.update_one(
        {"_id": ObjectId(id)},
        {
            "$push": {
                "comentarios": comentario,
                "historial": {
                    "accion": accion_historial,
                    "fecha": datetime.utcnow().isoformat()
                }
            }
        }
    )

    return jsonify({"message": "Comentario agregado", "comentario": comentario}), 201


def formatear_tarea(tarea):
    """Formatea una tarea para la respuesta JSON."""
    if not tarea:
        return None
    tarea_formateada = dict(tarea)
    tarea_formateada["_id"] = str(tarea_formateada["_id"])
    if "archivo" in tarea_formateada:
        tarea_formateada["archivoUrl"] = f"{request.host_url.rstrip('/')}/{tarea_formateada['archivo']}"
    if "prioridad" not in tarea_formateada:
        tarea_formateada["prioridad"] = "media"
    if "comentarios" not in tarea_formateada:
        tarea_formateada["comentarios"] = []
    if "historial" not in tarea_formateada:
        tarea_formateada["historial"] = []
    if "compartido_con" not in tarea_formateada:
        tarea_formateada["compartido_con"] = []
    return tarea_formateada
