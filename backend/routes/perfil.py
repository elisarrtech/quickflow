# routes/perfil.py
from flask import Blueprint, request, jsonify
from backend.auth_utils import token_required
from backend.models import users_collection

perfil_bp = Blueprint('perfil', __name__)

@perfil_bp.route('/api/perfil', methods=['GET'])
@token_required
def obtener_perfil(current_user):
    usuario = users_collection.find_one({"email": current_user})
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify({
        "email": usuario["email"],
        "nombre": usuario.get("nombre", "")
    }), 200

@perfil_bp.route('/api/perfil', methods=['PUT'])
@token_required
def actualizar_perfil(current_user):
    data = request.get_json()
    nuevo_nombre = data.get("nombre", "").strip()
    if not nuevo_nombre:
        return jsonify({"error": "Nombre requerido"}), 400

    result = users_collection.update_one(
        {"email": current_user},
        {"$set": {"nombre": nuevo_nombre}}
    )
    if result.modified_count == 1:
        return jsonify({"mensaje": "Nombre actualizado correctamente"}), 200
    else:
        return jsonify({"mensaje": "Sin cambios"}), 200
