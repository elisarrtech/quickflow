from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from backend.config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    CORS(app)

    # Importamos aquí para evitar dependencias circulares
    from backend.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

