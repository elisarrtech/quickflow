import jwt
from datetime import datetime, timedelta
from flask import current_app

def generate_token(email, expires_in=7200):
    payload = {
        "email": email,
        "exp": datetime.utcnow() + timedelta(seconds=expires_in),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")

def verify_token(token):
    try:
        payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        return payload["email"]
    except jwt.ExpiredSignatureError:
        print("❌ Token expirado")
        return None
    except jwt.InvalidTokenError:
        print("❌ Token inválido")
        return None
