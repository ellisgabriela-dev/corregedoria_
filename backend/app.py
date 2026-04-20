from flask import Flask
from config import Config
from extensions import db, jwt
from flask_cors import CORS

from routes.auth import auth_bp
from routes.boards import boards_bp
from routes.tasks import tasks_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
jwt.init_app(app)

CORS(app)

# 🔗 ROTAS
app.register_blueprint(auth_bp)
app.register_blueprint(boards_bp)
app.register_blueprint(tasks_bp)

# 📦 CRIAR BANCO (DEV)
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return {"msg": "API rodando 🚀"}

if __name__ == "__main__":
    app.run(debug=True)