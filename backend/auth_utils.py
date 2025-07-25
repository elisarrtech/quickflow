from functools import wraps
from flask import request, jsonify
from backend.jwt_utils import verify_token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'message': 'Token faltante'}), 401

        try:
            data = verify_token(token)
            current_user_email = data['email']
        except:
            return jsonify({'message': 'Token inválido o expirado'}), 401

        return f(current_user_email, *args, **kwargs)  # ✅ AQUI se pasa correctamente
    return decorated
