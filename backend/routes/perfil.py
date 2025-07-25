from flask import Blueprint, request, jsonify, current_app
from backend.auth_utils import token_required

perfil_bp = Blueprint('perfil', __name__)

@perfil_bp.route('/api/perfil', methods=['GET', 'PUT'])
@token_required
def perfil(current_user_email):
    db = current_app.mongo.db  # ✅ esta es la forma correcta
    users_collection = db.users  # o quickflowbase.users si así lo tienes

    if request.method == 'GET':
        user = users_collection.find_one({"email": current_user_email})
        if user:
            return jsonify({
                "email": user["email"],
                "nombre": user.get("nombre", "")
            }), 200
        return jsonify({"error": "Usuario no encontrado"}), 404

    elif request.method == 'PUT':
        data = request.get_json()
        nuevo_nombre = data.get("nombre")
        result = users_collection.update_one(
            {"email": current_user_email},
            {"$set": {"nombre": nuevo_nombre}}
        )
        if result.modified_count:
            return jsonify({"mensaje": "Nombre actualizado"}), 200
        else:
            return jsonify({"mensaje": "No se realizaron cambios"}), 200
