from flask import Blueprint, request, jsonify
from extensions import db
from models import Board, Column
from flask_jwt_extended import jwt_required, get_jwt_identity

boards_bp = Blueprint('boards', __name__, url_prefix='/api/boards')


# 🔹 SERIALIZADOR
def board_to_dict(board):
    return {
        "id": board.id,
        "title": board.title,
        "description": board.description,
        "columns_count": len(board.columns)
    }


# 📌 LISTAR BOARDS
@boards_bp.route('/', methods=['GET'])
@jwt_required()
def get_boards():
    user_id = get_jwt_identity()

    boards = Board.query.filter_by(user_id=user_id)\
        .order_by(Board.id.desc())\
        .all()

    return jsonify([board_to_dict(b) for b in boards])


# 📌 CRIAR BOARD
@boards_bp.route('/', methods=['POST'])
@jwt_required()
def create_board():
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data.get('title'):
        return jsonify({"detail": "Título é obrigatório"}), 400

    board = Board(
        title=data['title'],
        description=data.get('description', ''),
        user_id=user_id
    )

    db.session.add(board)
    db.session.commit()

    return jsonify(board_to_dict(board)), 201


# 📌 ATUALIZAR BOARD
@boards_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_board(id):
    user_id = get_jwt_identity()
    data = request.get_json()

    board = Board.query.filter_by(id=id, user_id=user_id).first()

    if not board:
        return jsonify({"detail": "Board não encontrado"}), 404

    if 'title' in data:
        board.title = data['title']

    if 'description' in data:
        board.description = data['description']

    db.session.commit()

    return jsonify(board_to_dict(board))


# 📌 DELETAR BOARD
@boards_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_board(id):
    user_id = get_jwt_identity()

    board = Board.query.filter_by(id=id, user_id=user_id).first()

    if not board:
        return jsonify({"detail": "Board não encontrado"}), 404

    db.session.delete(board)
    db.session.commit()

    return jsonify({"msg": "Board deletado com sucesso"})