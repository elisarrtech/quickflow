import jwt
from flask import request, jsonify
from functools import wraps
import os

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]

        if not token:
            return jsonify({'error': 'Token no proporcionado'}), 401

        try:
            data = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
            request.user_email = data['email']
        except Exception as e:
            return jsonify({'error': 'Token inválido'}), 401

        return f(*args, **kwargs)
    return decorated
