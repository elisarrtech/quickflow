# backend/routes/eventos_routes.py
from flask import Blueprint, request, jsonify
from bson import ObjectId
from backend.auth_utils import token_required
from backend.app import mongo
from datetime import datetime

eventos_bp = Blueprint("eventos", __name__)

# Validar tipo de evento
TIPOS_VALIDOS = ["reunion", "tarea", "recordatorio", "evento", "otro"]

def es_tipo_valido(tipo):
    return tipo in TIPOS_VALIDOS

# ✅ Obtener todos los eventos del usuario autenticado
@eventos_bp.route("/api/eventos", methods=["GET"])
@token_required
def obtener_eventos(usuario_actual):
    try:
        eventos = list(mongo.db.eventos.find({"email": usuario_actual}))
        for e in eventos:
            e["_id"] = str(e["_id"])
            # Asegurar campos opcionales
            if "tipo" not in e:
                e["tipo"] = "otro"
            if "participantes" not in e:
                e["participantes"] = []
        return jsonify(eventos), 200
    except Exception as e:
        print(f"❌ Error al obtener eventos: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

# ✅ Crear nuevo evento
@eventos_bp.route("/api/eventos", methods=["POST"])
@token_required
def crear_evento(usuario_actual):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se enviaron datos"}), 400

        titulo = data.get("titulo", "").strip()
        fecha = data.get("fecha", "").strip()
        hora = data.get("hora", "").strip()
        tipo = data.get("tipo", "reunion").lower()
        participantes = data.get("participantes", [])

        # Validaciones
        if not titulo:
            return jsonify({"error": "El título es obligatorio"}), 400
        if not fecha:
            return jsonify({"error": "La fecha es obligatoria"}), 400
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido. Usa YYYY-MM-DD"}), 400
        if not es_tipo_valido(tipo):
            return jsonify({"error": f"Tipo inválido. Usa uno de: {TIPOS_VALIDOS}"}), 400

        evento = {
            "email": usuario_actual,
            "titulo": titulo,
            "fecha": fecha,
            "hora": hora,
            "tipo": tipo,
            "participantes": participantes,
            "creado": datetime.utcnow(),
            "actualizado": datetime.utcnow()
        }

        resultado = mongo.db.eventos.insert_one(evento)
        evento["_id"] = str(resultado.inserted_id)
        return jsonify(evento), 201

    except Exception as e:
        print(f"❌ Error al crear evento: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

# ✅ Actualizar evento por ID
@eventos_bp.route("/api/eventos/<id>", methods=["PUT"])
@token_required
def actualizar_evento(usuario_actual, id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se enviaron datos"}), 400

        evento = mongo.db.eventos.find_one({"_id": ObjectId(id), "email": usuario_actual})
        if not evento:
            return jsonify({"error": "Evento no encontrado o no autorizado"}), 404

        # Validar tipo si se envía
        tipo = data.get("tipo", evento["tipo"]).lower()
        if not es_tipo_valido(tipo):
            return jsonify({"error": f"Tipo inválido. Usa uno de: {TIPOS_VALIDOS}"}), 400

        update_fields = {
            "titulo": data.get("titulo", evento["titulo"]).strip(),
            "fecha": data.get("fecha", evento["fecha"]).strip(),
            "hora": data.get("hora", evento["hora"]).strip(),
            "tipo": tipo,
            "participantes": data.get("participantes", evento["participantes"]),
            "actualizado": datetime.utcnow()
        }

        # Validar fecha
        try:
            datetime.strptime(update_fields["fecha"], "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido. Usa YYYY-MM-DD"}), 400

        mongo.db.eventos.update_one({"_id": ObjectId(id)}, {"$set": update_fields})
        evento.update(update_fields)
        evento["_id"] = str(evento["_id"])
        return jsonify(evento), 200

    except Exception as e:
        print(f"❌ Error al actualizar evento: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

# ✅ Eliminar evento por ID
@eventos_bp.route("/api/eventos/<id>", methods=["DELETE"])
@token_required
def eliminar_evento(usuario_actual, id):
    try:
        evento = mongo.db.eventos.find_one({"_id": ObjectId(id), "email": usuario_actual})
        if not evento:
            return jsonify({"error": "Evento no encontrado o no autorizado"}), 404

        mongo.db.eventos.delete_one({"_id": ObjectId(id)})
        return jsonify({"mensaje": "Evento eliminado correctamente ✅"}), 200

    except Exception as e:
        print(f"❌ Error al eliminar evento: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500
