from functools import wraps
from flask import request, jsonify
import jwt
from jwt_utils import verify_token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'OPTIONS':
            return '', 204

        auth_header = request.headers.get('Authorization', '')
        parts = auth_header.split()

        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Formato del token inválido'}), 401

        token = parts[1]

        if not token:
            return jsonify({'error': 'Token no proporcionado'}), 401

        try:
            user_email = verify_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401
        except Exception as e:
            return jsonify({'error': f'Error al verificar token: {str(e)}'}), 401

        return f(user_email, *args, **kwargs)
    return decorated
