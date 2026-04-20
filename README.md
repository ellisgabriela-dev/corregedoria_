# TaskFlow 🚀

Sistema de gerenciamento de tarefas estilo Trello com cadastro de usuários, categorias de demanda e urgência.

## Stack
- **Backend:** Python + FastAPI
- **Banco de dados:** PostgreSQL
- **Frontend:** HTML/CSS/JS (vanilla, sem dependências)

---

## 1. Configurar o banco de dados

```bash
# Crie o banco
psql -U postgres -c "CREATE DATABASE taskflow;"

# Execute o schema
psql -U postgres -d taskflow -f database/schema.sql
```

---

## 2. Configurar o backend

```bash
cd backend

# Crie o .env
cp .env.example .env
# Edite .env com suas credenciais do PostgreSQL

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate   # Linux/Mac
# ou: venv\Scripts\activate   # Windows

# Instale as dependências
pip install -r requirements.txt

# Inicie o servidor
uvicorn main:app --reload --port 8000
```

A API estará disponível em: http://localhost:8000
Documentação interativa: http://localhost:8000/docs

---

## 3. Rodar o frontend

Abra o arquivo `frontend/index.html` diretamente no navegador,
ou sirva com qualquer servidor estático:

```bash
# Com Python
cd frontend
python -m http.server 3000
# Acesse: http://localhost:3000
```

---

## Funcionalidades

- ✅ Cadastro e login de usuários (JWT)
- ✅ Criar/listar múltiplos quadros (boards)
- ✅ Colunas configuráveis por quadro
- ✅ Tarefas com:
  - Título e descrição
  - **Tipo de demanda** (configurável pelo usuário)
  - **Urgência:** Urgente 🔴 / Médio 🟡 / Não Urgente 🟢
  - Responsável
  - Data de prazo
  - Comentários e tags
- ✅ Histórico de atividades no banco
- ✅ Tipos de demanda padrão (Bug, Nova Funcionalidade, Melhoria, Suporte, Documentação, Infraestrutura)
- ✅ Usuário pode criar seus próprios tipos de demanda

---

## Estrutura do projeto

```
taskflow/
├── database/
│   └── schema.sql          # Schema completo PostgreSQL
├── backend/
│   ├── main.py             # Entrypoint FastAPI
│   ├── database.py         # Models SQLAlchemy + conexão
│   ├── requirements.txt
│   ├── .env.example
│   └── routers/
│       ├── auth.py         # Login/registro (JWT)
│       ├── users.py
│       ├── boards.py
│       ├── columns.py
│       ├── tasks.py
│       └── demand_types.py
└── frontend/
    └── index.html          # App completo (SPA)
```

---

## Endpoints principais

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | /api/auth/register | Cadastrar usuário |
| POST | /api/auth/login | Login (retorna JWT) |
| GET | /api/boards/ | Listar quadros |
| POST | /api/boards/ | Criar quadro |
| GET | /api/boards/{id} | Quadro com colunas e tarefas |
| POST | /api/tasks/ | Criar tarefa |
| PATCH | /api/tasks/{id} | Atualizar tarefa |
| DELETE | /api/tasks/{id} | Excluir tarefa |
| GET | /api/demand-types/ | Listar tipos de demanda |
| POST | /api/demand-types/ | Criar tipo personalizado |
