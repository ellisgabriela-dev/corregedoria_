from flask import Blueprint, request, jsonify
from extensions import db
from models import User
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
import random

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def random_color():
    colors = ["#4f8ef7", "#7c5cfc", "#f43f5e", "#10b981"]
    return random.choice(colors)

# REGISTER
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}

    if not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({"detail": "Preencha todos os campos"}), 400

    email = data['email'].lower()

    if User.query.filter_by(email=email).first():
        return jsonify({"detail": "Usuário já existe"}), 400

    user = User(
        name=data['name'],
        email=email,
        password=generate_password_hash(data['password']),
        avatar_color=random_color()
    )

    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))

    return jsonify({
        "access_token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "avatar_color": user.avatar_color
        }
    })


# LOGIN
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}

    if not data.get('email') or not data.get('password'):
        return jsonify({"detail": "Campos obrigatórios"}), 400

    email = data['email'].lower()

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"detail": "Credenciais inválidas"}), 401

    token = create_access_token(identity=str(user.id))

    return jsonify({
        "access_token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "avatar_color": user.avatar_color
        }
    })