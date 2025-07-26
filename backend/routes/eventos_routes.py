
# backend/eventos_routes.py
from flask import Blueprint, request, jsonify
from flask_pymongo import ObjectId
from backend.jwt_utils import verify_token
from backend.auth_utils import token_required
from backend.app import mongo  # ✅ Aquí es donde estaba el error
from datetime import datetime

eventos_bp = Blueprint('eventos', __name__)

# 🟢 Obtener todos los eventos del usuario autenticado
@eventos_bp.route('/api/eventos', methods=['GET'])
@token_required
def obtener_eventos(usuario_actual):
    eventos = list(mongo.db.eventos.find({ "email": usuario_actual }))
    for e in eventos:
        e["_id"] = str(e["_id"])
    return jsonify(eventos), 200

# 🟢 Crear un nuevo evento
@eventos_bp.route('/api/eventos', methods=['POST'])
@token_required
def crear_evento(usuario_actual):
    data = request.get_json()
    evento = {
        "email": usuario_actual,
        "titulo": data.get("titulo", ""),
        "fecha": data.get("fecha", ""),
        "hora": data.get("hora", ""),
        "tipo": data.get("tipo", "reunion"),
        "participantes": data.get("participantes", []),
        "creado": datetime.utcnow()
    }
    resultado = mongo.db.eventos.insert_one(evento)
    evento["_id"] = str(resultado.inserted_id)
    return jsonify(evento), 201

# 🟢 Actualizar evento por ID
@eventos_bp.route('/api/eventos/<id>', methods=['PUT'])
@token_required
def actualizar_evento(usuario_actual, id):
    data = request.get_json()
    evento = mongo.db.eventos.find_one({"_id": ObjectId(id), "email": usuario_actual})
    if not evento:
        return jsonify({"error": "Evento no encontrado"}), 404
    
    update_fields = {
        "titulo": data.get("titulo", evento["titulo"]),
        "fecha": data.get("fecha", evento["fecha"]),
        "hora": data.get("hora", evento["hora"]),
        "tipo": data.get("tipo", evento["tipo"]),
        "participantes": data.get("participantes", evento["participantes"])
    }

    mongo.db.eventos.update_one({"_id": ObjectId(id)}, {"$set": update_fields})
    return jsonify({"mensaje": "Evento actualizado"}), 200

# 🟢 Eliminar evento por ID
@eventos_bp.route('/api/eventos/<id>', methods=['DELETE'])
@token_required
def eliminar_evento(usuario_actual, id):
    evento = mongo.db.eventos.find_one({"_id": ObjectId(id), "email": usuario_actual})
    if not evento:
        return jsonify({"error": "Evento no encontrado"}), 404
    
    mongo.db.eventos.delete_one({"_id": ObjectId(id)})
    return jsonify({"mensaje": "Evento eliminado"}), 200
