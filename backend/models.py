from extensions import db
from datetime import datetime

# 👤 USER
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    avatar_color = db.Column(db.String(20), default="#4f8ef7")

    boards = db.relationship('Board', backref='user', lazy=True, cascade="all, delete")


# 📋 BOARD
class Board(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    columns = db.relationship('Column', backref='board', lazy=True, cascade="all, delete")


# 📊 COLUMN
class Column(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'), nullable=False)

    tasks = db.relationship('Task', backref='column', lazy=True, cascade="all, delete")


# ✅ TASK
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    column_id = db.Column(db.Integer, db.ForeignKey('column.id'), nullable=False)
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'), nullable=False)

    urgency = db.Column(db.String(20), default="medio")

    due_date = db.Column(db.Date)

    completed = db.Column(db.Boolean, default=False)
    position = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)