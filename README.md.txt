# 📌 Agenda Corregedoria

Sistema web para gerenciamento de tarefas, prazos e demandas, com autenticação segura e dashboard interativo.

---

## 🚀 Tecnologias utilizadas

* 🐍 Python com Flask
* 🐘 PostgreSQL
* 🔐 JWT (autenticação segura)
* 🎨 HTML, CSS e JavaScript
* 📊 Chart.js (dashboard)

---

## 📂 Estrutura do projeto

```
agenda-corregedoria/
│
├── backend/
│   ├── app.py
│   ├── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   ├── script.js
│
└── README.md
```

---

## ⚙️ Funcionalidades

✔ Cadastro e login de usuários
✔ Autenticação com token (JWT)
✔ Criação de tarefas
✔ Marcar como concluída
✔ Exclusão de tarefas
✔ Filtro por categoria
✔ Dashboard com indicadores
✔ Gráficos de prioridade e categoria

---

## 🔐 Autenticação

O sistema utiliza JWT para proteger as rotas.

Após o login, o token deve ser enviado no header:

```
Authorization: Bearer SEU_TOKEN
```

---

## 🧪 Rotas da API

### 🔹 Login

```
POST /login
```

### 🔹 Registro

```
POST /register
```

### 🔹 Listar tarefas

```
GET /tarefas
```

### 🔹 Criar tarefa

```
POST /tarefas
```

### 🔹 Atualizar tarefa

```
PUT /tarefas/{id}
```

### 🔹 Deletar tarefa

```
DELETE /tarefas/{id}
```

---

## 🛠️ Como rodar localmente

### 1. Clonar o repositório

```
git clone https://github.com/seu-usuario/seu-repo.git
```

### 2. Acessar o backend

```
cd backend
```

### 3. Criar ambiente virtual

```
python -m venv venv
venv\Scripts\activate
```

### 4. Instalar dependências

```
pip install -r requirements.txt
```

### 5. Criar variável de ambiente

Crie um arquivo `.env` com:

```
DATABASE_URL=sua_url_do_render
JWT_SECRET_KEY=sua_chave_secreta
```

### 6. Rodar o servidor

```
python app.py
```

---

## 🌐 Deploy

O projeto pode ser hospedado na plataforma Render:

* Backend como Web Service
* Frontend como Static Site
* Banco PostgreSQL integrado

---

## 👩‍💻 Autora

Gabriela Gomes - PrismCode
Projeto desenvolvido para organização de tarefas da Corregedoria.

---

## 📄 Licença

Este projeto é de uso interno/educacional.
