from functools import wraps
from flask import request, jsonify

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'OPTIONS':
            return '', 204  # ✅ Permitir preflight sin token

        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'msg': 'Token no proporcionado'}), 401

        try:
            from jwt_utils import verify_token
            user_email = verify_token(token)
        except:
            return jsonify({'msg': 'Token inválido o expirado'}), 401

        return f(user_email, *args, **kwargs)
    return decorated
