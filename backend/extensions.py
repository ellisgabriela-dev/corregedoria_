from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask import jsonify

db = SQLAlchemy()
jwt = JWTManager()

# 🔐 ERROS JWT CUSTOMIZADOS
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"detail": "Token expirado"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"detail": "Token inválido"}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({"detail": "Token obrigatório"}), 401