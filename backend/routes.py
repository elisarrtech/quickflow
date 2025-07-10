from flask import Blueprint, jsonify, request
from functools import wraps
from backend.app import db
from backend.models import Task, User
from backend.auth import hash_password, check_password, generate_token, verify_token

api_bp = Blueprint('api', __name__)

# =============== Middleware Token JWT ===================
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            parts = request.headers['Authorization'].split(" ")
            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]

        if not token:
            return jsonify({'message': 'Token faltante'}), 401

        user_id = verify_token(token)
        if not user_id:
            return jsonify({'message': 'Token inválido o expirado'}), 401

        return f(user_id, *args, **kwargs)
    return decorated

# =============== Rutas Auth ===================
@api_bp.route('/register', methods=['POST'])
def register():
    data = request.json

    # Validaciones mínimas
    if not data.get('email') or not data.get('password'):
        return {"message": "Email y password son requeridos"}, 400

    # Verificar si ya existe
    if User.query.filter_by(email=data['email']).first():
        return {"message": "Email ya registrado"}, 400

    # Crear usuario
    hashed_password = hash_password(data['password'])
    user = User(email=data['email'], password=hashed_password)  # 👈 eliminamos username
    db.session.add(user)
    db.session.commit()

    return {"message": "Usuario registrado correctamente"}, 201


@api_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and check_password(user.password, data['password']):
        token = generate_token(user.id)
        return {"token": token}
    return {"message": "Credenciales inválidas"}, 401

# =============== Rutas Protegidas ===================
@api_bp.route('/tasks', methods=['GET'])
@token_required
def get_tasks(user_id):
    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify([{'id': t.id, 'title': t.title, 'completed': t.completed} for t in tasks])

@api_bp.route('/tasks', methods=['POST'])
@token_required
def create_task(user_id):
    data = request.json
    new_task = Task(
        title=data['title'],
        description=data.get('description'),
        user_id=user_id
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'message': 'Task created successfully'}), 201
