# backend/routes/perfil.py
from flask import Blueprint, request, jsonify, current_app
from backend.auth_utils import token_required

perfil_bp = Blueprint('perfil', __name__)

@perfil_bp.route('/perfil', methods=['GET', 'PUT'])
@token_required
def perfil(current_user_email):
    db = current_app.mongo.db
    users_collection = db.users

    if request.method == 'GET':
        user = users_collection.find_one({"email": current_user_email})
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        return jsonify({
            "email": user["email"],
            "nombre": user.get("nombre", "").strip(),
            "foto": user.get("foto", "")  # Por si agregas foto en el futuro
        }), 200

    elif request.method == 'PUT':
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No se enviaron datos"}), 400

            nuevo_nombre = data.get("nombre", "").strip()
            if not nuevo_nombre:
                return jsonify({"error": "Nombre no proporcionado o vacío"}), 400

            if len(nuevo_nombre) > 50:
                return jsonify({"error": "El nombre es demasiado largo"}), 400

            result = users_collection.update_one(
                {"email": current_user_email},
                {"$set": {"nombre": nuevo_nombre}}
            )

            if result.modified_count > 0:
                return jsonify({"mensaje": "Nombre actualizado correctamente ✅"}), 200
            else:
                # Podría no haber cambios si ya tenía ese nombre
                return jsonify({"mensaje": "No se realizaron cambios (posiblemente ya tenía ese nombre)"}), 200

        except Exception as e:
            current_app.logger.error(f"❌ Error actualizando perfil: {str(e)}")
            return jsonify({"error": "Error interno del servidor"}), 500
