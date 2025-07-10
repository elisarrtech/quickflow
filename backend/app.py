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

    # 🔑 Esta línea crea las tablas si no existen
    with app.app_context():
        db.create_all()

    # Registro de Blueprints
    from backend.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.route('/')
    def index():
        return {"status": "Backend Flask funcionando correctamente 🚀"}

    return app
