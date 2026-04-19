from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

# 🔐 JWT
app.config["JWT_SECRET_KEY"] = "super-secret-key"
jwt = JWTManager(app)

# 🔌 CONEXÃO BANCO
def get_conn():
    return psycopg2.connect(
        os.getenv("DATABASE_URL"),
        sslmode='require'
    )

# =========================
# 🧱 CRIAÇÃO DAS TABELAS
# =========================
with get_conn() as conn:
    with conn.cursor() as cur:

        cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
          id SERIAL PRIMARY KEY,
          usuario TEXT UNIQUE,
          senha TEXT
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
          id SERIAL PRIMARY KEY,
          texto TEXT,
          data DATE,
          categoria TEXT,
          prioridade TEXT,
          concluida BOOLEAN DEFAULT false
        )
        """)

        conn.commit()

# =========================
# 🔐 AUTH
# =========================

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        if not data or not data.get("usuario") or not data.get("senha"):
            return jsonify({"erro": "Dados obrigatórios"}), 400

        senha_hash = generate_password_hash(data['senha'])

        conn = get_conn()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO usuarios (usuario, senha) VALUES (%s,%s)",
            (data['usuario'], senha_hash)
        )

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"mensagem": "Usuário criado"}), 201

    except Exception as e:
        return jsonify({"erro": "Usuário já existe"}), 400


@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        conn = get_conn()
        cur = conn.cursor()

        cur.execute(
            "SELECT id, senha FROM usuarios WHERE usuario=%s",
            (data['usuario'],)
        )

        user = cur.fetchone()

        cur.close()
        conn.close()

        if not user or not check_password_hash(user[1], data['senha']):
            return jsonify({"erro": "Login inválido"}), 401

        token = create_access_token(identity=user[0])

        return jsonify({"token": token})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# =========================
# 📋 TAREFAS
# =========================

@app.route('/tarefas', methods=['GET'])
@jwt_required()
def get_tarefas():
    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("SELECT * FROM tarefas ORDER BY id DESC")
        rows = cur.fetchall()

        tarefas = [
            {
                "id": r[0],
                "texto": r[1],
                "data": r[2].isoformat() if r[2] else None,
                "categoria": r[3],
                "prioridade": r[4],
                "concluida": r[5]
            }
            for r in rows
        ]

        cur.close()
        conn.close()

        return jsonify(tarefas), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/tarefas', methods=['POST'])
@jwt_required()
def add_tarefa():
    try:
        data = request.get_json()

        if not data or not data.get("texto"):
            return jsonify({"erro": "Texto obrigatório"}), 400

        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO tarefas (texto, data, categoria, prioridade)
            VALUES (%s,%s,%s,%s)
            RETURNING id
        """, (
            data.get("texto"),
            data.get("data"),
            data.get("categoria"),
            data.get("prioridade")
        ))

        new_id = cur.fetchone()[0]

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            "mensagem": "Tarefa criada",
            "id": new_id
        }), 201

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/tarefas/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_tarefa(id):
    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("DELETE FROM tarefas WHERE id=%s RETURNING id", (id,))
        deleted = cur.fetchone()

        conn.commit()
        cur.close()
        conn.close()

        if not deleted:
            return jsonify({"erro": "Tarefa não encontrada"}), 404

        return jsonify({"mensagem": "Tarefa deletada"}), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route('/tarefas/<int:id>', methods=['PUT'])
@jwt_required()
def toggle_tarefa(id):
    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            UPDATE tarefas
            SET concluida = NOT concluida
            WHERE id=%s
            RETURNING concluida
        """, (id,))

        result = cur.fetchone()

        conn.commit()
        cur.close()
        conn.close()

        if not result:
            return jsonify({"erro": "Tarefa não encontrada"}), 404

        return jsonify({
            "mensagem": "Atualizado",
            "concluida": result[0]
        }), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
