from flask import Blueprint, request, jsonify
from backend.app import db
from backend.models import Task

api_bp = Blueprint('api', __name__)

@api_bp.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([{'id': t.id, 'title': t.title, 'completed': t.completed} for t in tasks])

@api_bp.route('/tasks', methods=['POST'])
def create_task():
    data = request.json
    new_task = Task(title=data['title'], description=data.get('description'), user_id=data['user_id'])
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'message': 'Task created successfully'}), 201

from backend.auth import hash_password, check_password, generate_token, verify_token
from backend.models import User
from flask import request

@api_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    hashed_password = hash_password(data['password'])
    user = User(username=data['username'], email=data['email'], password=hashed_password)
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

from functools import wraps
from flask import request, jsonify

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # Bearer <token>

        if not token:
            return jsonify({'message': 'Token faltante'}), 401

        user_id = verify_token(token)
        if not user_id:
            return jsonify({'message': 'Token inválido o expirado'}), 401

        return f(user_id, *args, **kwargs)
    return decorated

