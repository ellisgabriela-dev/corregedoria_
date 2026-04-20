from flask import Flask
from flask_cors import CORS
from extensions import db, jwt
from routes.auth import auth_bp
from routes.boards import boards_bp
from routes.tasks import tasks_bp
import os

app = Flask(__name__)

# 🔐 CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'sqlite:///database.db'
)

app.config['JWT_SECRET_KEY'] = os.getenv(
    'JWT_SECRET_KEY',
    'dev-secret'
)

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600

# 🔌 INIT
db.init_app(app)
jwt.init_app(app)

CORS(app, origins=["*"])  # depois restringe

# 📦 (DEV ONLY)
with app.app_context():
    db.create_all()

# 🔗 ROTAS
app.register_blueprint(auth_bp)
app.register_blueprint(boards_bp)
app.register_blueprint(tasks_bp)

# 🚀 START
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)