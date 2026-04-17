const express = require('express');
const { Pool } = require('pg');
const cors = require('cors');
const bcrypt = require('bcrypt');

const app = express();

app.use(cors());
app.use(express.json());

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false }
});

/* TESTE DE CONEXÃO */
pool.connect()
  .then(() => console.log("Conectado ao banco"))
  .catch(err => console.error("Erro na conexão:", err));

/* CRIAR TABELAS */
(async () => {
  try {

    await pool.query(`
      CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        usuario TEXT UNIQUE,
        senha TEXT
      )
    `);

    // 🔐 senha com hash
    const senhaHash = await bcrypt.hash('12345', 10);

    await pool.query(`
      INSERT INTO usuarios (usuario, senha)
      VALUES ($1, $2)
      ON CONFLICT (usuario) DO NOTHING;
    `, ['admin', senhaHash]);

    await pool.query(`
      CREATE TABLE IF NOT EXISTS tarefas (
        id SERIAL PRIMARY KEY,
        texto TEXT,
        data DATE,
        categoria TEXT,
        prioridade TEXT,
        concluida BOOLEAN DEFAULT false,
        usuario_id INTEGER
      )
    `);

    console.log("Tabelas prontas");

  } catch (err) {
    console.error(err);
  }
})();


// =========================
// USUÁRIOS
// =========================

// cadastro
app.post('/register', async (req,res)=>{
  const { usuario, senha } = req.body;

  try{
    const hash = await bcrypt.hash(senha, 10);

    await pool.query(
      'INSERT INTO usuarios (usuario, senha) VALUES ($1, $2)',
      [usuario, hash]
    );

    res.send("Usuário criado");
  }catch{
    res.status(400).send("Usuário já existe");
  }
});


// login (CORRIGIDO)
app.post('/login', async (req,res)=>{
  const { usuario, senha } = req.body;

  try{
    const result = await pool.query(
      'SELECT * FROM usuarios WHERE usuario=$1',
      [usuario]
    );

    if(result.rows.length === 0){
      return res.status(401).send("Usuário não encontrado");
    }

    const user = result.rows[0];

    const senhaValida = await bcrypt.compare(senha, user.senha);

    if(!senhaValida){
      return res.status(401).send("Senha incorreta");
    }

    res.json(user);

  }catch(err){
    res.status(500).send("Erro no servidor");
  }
});


// =========================
// TAREFAS
// =========================

// buscar
app.get('/tarefas/:usuario_id', async (req,res)=>{
  const result = await pool.query(
    'SELECT * FROM tarefas WHERE usuario_id=$1 ORDER BY id DESC',
    [req.params.usuario_id]
  );

  res.json(result.rows);
});

// criar
app.post('/tarefas', async (req,res)=>{
  const { texto, data, categoria, prioridade, usuario_id } = req.body;

  await pool.query(
    'INSERT INTO tarefas (texto,data,categoria,prioridade,usuario_id) VALUES ($1,$2,$3,$4,$5)',
    [texto,data,categoria,prioridade,usuario_id]
  );

  res.send("Salvo");
});

// deletar
app.delete('/tarefas/:id', async (req,res)=>{
  await pool.query('DELETE FROM tarefas WHERE id=$1',[req.params.id]);
  res.send("Deletado");
});

// concluir
app.put('/tarefas/:id', async (req,res)=>{
  await pool.query(
    'UPDATE tarefas SET concluida = NOT concluida WHERE id=$1',
    [req.params.id]
  );
  res.send("Atualizado");
});


app.get('/', (req,res)=>{
  res.send("API rodando 🚀");
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, ()=>{
  console.log("Servidor rodando");
});
