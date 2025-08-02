from functools import wraps
from flask import request, jsonify
import jwt

# Asegúrate de que esta función esté bien definida en jwt_utils.py
from backend.jwt_utils import verify_token


def token_required(f):
    """
    Decorador para proteger rutas que requieren autenticación JWT.
    Extrae el token del encabezado 'Authorization: Bearer <token>'
    y verifica su validez antes de permitir el acceso.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Manejar preflight (OPTIONS) para CORS
        if request.method == 'OPTIONS':
            return '', 204

        # Obtener el encabezado de autorización
        auth_header = request.headers.get('Authorization', '').strip()
        if not auth_header:
            return jsonify({'error': 'Token no proporcionado'}), 401

        # Validar formato del encabezado: "Bearer <token>"
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Formato del token inválido. Usa "Bearer <token>"'}), 401

        token = parts[1]

        # Verificar el token usando tu función personalizada
        try:
            user_email = verify_token(token)
            if not user_email:
                return jsonify({'error': 'Token inválido o sin email'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({'error': f'Token inválido: {str(e)}'}), 401
        except Exception as e:
            # Solo para errores inesperados (problemas de decoding, claves, etc.)
            print(f"Error inesperado al verificar token: {e}")
            return jsonify({'error': 'Error interno al verificar el token'}), 500

        # Llamar a la función original con el email del usuario
        return f(user_email, *args, **kwargs)

    return decorated
