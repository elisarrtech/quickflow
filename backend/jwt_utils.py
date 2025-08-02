# backend/jwt_utils.py
import jwt
from datetime import datetime, timedelta
from flask import current_app, current_app
from werkzeug.security import generate_password_hash, check_password_hash

# --- Generar Token JWT ---
def generate_token(email, expires_in=7200):
    """
    Genera un token JWT para un usuario.
    :param email: Correo del usuario (identificador)
    :param expires_in: Tiempo de expiración en segundos (2 horas por defecto)
    :return: Token codificado
    """
    payload = {
        "email": email,
        "exp": datetime.utcnow() + timedelta(seconds=expires_in),
        "iat": datetime.utcnow()
    }
    try:
        token = jwt.encode(
            payload,
            current_app.config["SECRET_KEY"],
            algorithm="HS256"
        )
        # En PyJWT >= 2.0, jwt.encode devuelve un string
        return token
    except Exception as e:
        print(f"❌ Error al generar token: {e}")
        return None

# --- Verificar Token JWT ---
def verify_token(token):
    """
    Verifica un token JWT y devuelve el email del usuario si es válido.
    :param token: Token JWT
    :return: email del usuario o None si es inválido o expirado
    """
    if not token:
        return None

    try:
        payload = jwt.decode(
            token,
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"]
        )
        return payload["email"]
    except jwt.ExpiredSignatureError:
        print("❌ Token expirado")
        return None
    except jwt.InvalidTokenError as e:
        print(f"❌ Token inválido: {e}")
        return None
    except Exception as e:
        print(f"❌ Error inesperado al verificar token: {e}")
        return None

# --- Hash de contraseñas ---
def hash_password(password):
    """
    Genera un hash seguro de una contraseña.
    :param password: Contraseña en texto plano
    :return: Hash de la contraseña
    """
    if not password:
        raise ValueError("La contraseña no puede ser vacía")
    return generate_password_hash(password)

# --- Verificar contraseña ---
def check_password(hashed_password, password):
    """
    Verifica si una contraseña coincide con su hash.
    :param hashed_password: Hash almacenado
    :param password: Contraseña en texto plano
    :return: True si coincide, False si no
    """
    if not hashed_password or not password:
        return False
    return check_password_hash(hashed_password, password)
