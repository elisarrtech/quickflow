import jwt
from flask import request, jsonify
from functools import wraps
import os

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split()[1]

        if not token:
            return jsonify({'error': 'Token no proporcionado'}), 401

        try:
            secret = os.getenv("SECRET_KEY")
            if not secret:
                return jsonify({'error': 'Clave secreta no configurada'}), 500

            data = jwt.decode(token, secret, algorithms=["HS256"])
            request.user_email = data.get('email')

            if not request.user_email:
                return jsonify({'error': 'Token sin email válido'}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'El token ha expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401
        except Exception as e:
            return jsonify({'error': f'Error al verificar token: {str(e)}'}), 500

        return f(*args, **kwargs)
    return decorated
