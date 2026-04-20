from flask import Blueprint, request, jsonify
from extensions import db
from models import Task, Column
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')


# 🔹 FUNÇÃO AUXILIAR (CONVERTER DATA)
def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        return None


# 🔹 SERIALIZADOR (PADRÃO FRONT)
def task_to_dict(task):
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "urgency": task.urgency,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "column_id": task.column_id
    }


# 🔹 CRIAR TASK
@tasks_bp.route('/', methods=['POST'])
@jwt_required()
def create_task():
    data = request.get_json()
    user_id = get_jwt_identity()

    column = Column.query.get(data['column_id'])

    if not column:
        return jsonify({"detail": "Coluna não encontrada"}), 404

    # 🔒 segurança
    if column.board.user_id != user_id:
        return jsonify({"detail": "Acesso negado"}), 403

    due_date = parse_date(data.get('due_date'))

    task = Task(
        title=data['title'],
        description=data.get('description'),
        column_id=data['column_id'],
        urgency=data.get('urgency', 'medio'),
        due_date=due_date
    )

    db.session.add(task)
    db.session.commit()

    return jsonify(task_to_dict(task)), 201


# 🔹 LISTAR TASKS DE UMA COLUNA
@tasks_bp.route('/column/<int:column_id>', methods=['GET'])
@jwt_required()
def get_tasks(column_id):
    user_id = get_jwt_identity()

    column = Column.query.get(column_id)

    if not column:
        return jsonify({"detail": "Coluna não encontrada"}), 404

    # 🔒 segurança
    if column.board.user_id != user_id:
        return jsonify({"detail": "Acesso negado"}), 403

    tasks = Task.query.filter_by(column_id=column_id)\
        .order_by(Task.created_at)\
        .all()

    return jsonify([task_to_dict(t) for t in tasks])


# 🔹 ATUALIZAR TASK
@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    data = request.get_json()
    user_id = get_jwt_identity()

    task = Task.query.get(task_id)

    if not task:
        return jsonify({"detail": "Tarefa não encontrada"}), 404

    # 🔒 segurança
    if task.column.board.user_id != user_id:
        return jsonify({"detail": "Acesso negado"}), 403

    if 'title' in data:
        task.title = data['title']

    if 'description' in data:
        task.description = data['description']

    if 'urgency' in data:
        task.urgency = data['urgency']

    if 'due_date' in data:
        task.due_date = parse_date(data['due_date'])

    db.session.commit()

    return jsonify(task_to_dict(task))


# 🔹 DELETAR TASK
@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    user_id = get_jwt_identity()

    task = Task.query.get(task_id)

    if not task:
        return jsonify({"detail": "Tarefa não encontrada"}), 404

    # 🔒 segurança
    if task.column.board.user_id != user_id:
        return jsonify({"detail": "Acesso negado"}), 403

    db.session.delete(task)
    db.session.commit()

    return jsonify({"msg": "Deletado com sucesso"})

@tasks_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    user_id = get_jwt_identity()

    task = Task.query.get(task_id)

    if not task:
        return jsonify({"detail": "Tarefa não encontrada"}), 404

    if task.column.board.user_id != user_id:
        return jsonify({"detail": "Acesso negado"}), 403

    return jsonify({
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "urgency": task.urgency,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "column_id": task.column_id
    })