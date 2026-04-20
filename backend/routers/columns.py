from flask import Blueprint, request, jsonify
from extensions import db
from models import Column, Board
from flask_jwt_extended import jwt_required, get_jwt_identity

columns_bp = Blueprint('columns', __name__, url_prefix='/api/columns')


# 🔹 SERIALIZADOR
def column_to_dict(column):
    return {
        "id": column.id,
        "title": column.title,
        "board_id": column.board_id
    }


# 📌 LISTAR COLUNAS
@columns_bp.route('/board/<int:board_id>', methods=['GET'])
@jwt_required()
def get_columns(board_id):
    user_id = get_jwt_identity()

    board = Board.query.filter_by(id=board_id, user_id=user_id).first()
    if not board:
        return jsonify({"detail": "Board não encontrado"}), 404

    columns = Column.query.filter_by(board_id=board_id)\
        .order_by(Column.id)\
        .all()

    return jsonify([column_to_dict(c) for c in columns])


# 📌 CRIAR COLUNA
@columns_bp.route('/', methods=['POST'])
@jwt_required()
def create_column():
    user_id = get_jwt_identity()
    data = request.get_json()

    board = Board.query.filter_by(id=data.get('board_id'), user_id=user_id).first()
    if not board:
        return jsonify({"detail": "Board não encontrado"}), 404

    if not data.get('title'):
        return jsonify({"detail": "Título é obrigatório"}), 400

    column = Column(
        title=data['title'],
        board_id=data['board_id']
    )

    db.session.add(column)
    db.session.commit()

    return jsonify(column_to_dict(column)), 201


# 📌 ATUALIZAR COLUNA
@columns_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_column(id):
    user_id = get_jwt_identity()
    data = request.get_json()

    column = Column.query.get(id)

    if not column:
        return jsonify({"detail": "Coluna não encontrada"}), 404

    board = Board.query.filter_by(id=column.board_id, user_id=user_id).first()
    if not board:
        return jsonify({"detail": "Acesso negado"}), 403

    if 'title' in data:
        column.title = data['title']

    db.session.commit()

    return jsonify(column_to_dict(column))


# 📌 DELETAR COLUNA
@columns_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_column(id):
    user_id = get_jwt_identity()

    column = Column.query.get(id)

    if not column:
        return jsonify({"detail": "Coluna não encontrada"}), 404

    board = Board.query.filter_by(id=column.board_id, user_id=user_id).first()
    if not board:
        return jsonify({"detail": "Acesso negado"}), 403

    db.session.delete(column)
    db.session.commit()

    return jsonify({"msg": "Coluna deletada com sucesso"})