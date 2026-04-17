const express = require('express');
const { Pool } = require('pg');
const cors = require('cors');

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

/* CRIAR TABELA */
(async () => {
  try {
    await pool.query(`
      CREATE TABLE IF NOT EXISTS tarefas (
        id SERIAL PRIMARY KEY,
        texto TEXT,
        data DATE,
        categoria TEXT,
        prioridade TEXT,
        concluida BOOLEAN DEFAULT false
      )
    `);
    console.log("Tabela pronta");
  } catch (err) {
    console.error(err);
  }
})();

/* ROTAS */

app.get('/tarefas', async (req,res)=>{
  const result = await pool.query('SELECT * FROM tarefas ORDER BY id DESC');
  res.json(result.rows);
});

app.post('/tarefas', async (req,res)=>{
  const { texto, data, categoria, prioridade } = req.body;

  await pool.query(
    'INSERT INTO tarefas (texto,data,categoria,prioridade) VALUES ($1,$2,$3,$4)',
    [texto,data,categoria,prioridade]
  );

  res.send("Salvo");
});

app.delete('/tarefas/:id', async (req,res)=>{
  await pool.query('DELETE FROM tarefas WHERE id=$1',[req.params.id]);
  res.send("Deletado");
});

app.put('/tarefas/:id', async (req,res)=>{
  await pool.query(
    'UPDATE tarefas SET concluida = NOT concluida WHERE id=$1',
    [req.params.id]
  );
  res.send("Atualizado");
});

/* PORTA CORRETA */
const PORT = process.env.PORT || 3000;

app.listen(PORT, ()=>{
  console.log("Servidor rodando");
});
