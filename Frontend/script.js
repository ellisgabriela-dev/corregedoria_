/* =========================
🔧 CONFIG GLOBAL
========================= */

const API = "https://corregedoriaback.onrender.com";

let tasks = [];
let filtroAtual = "";

/* =========================
🔐 LOGIN
========================= */

async function entrar(){

  let usuario = document.getElementById("usuario").value;
  let senha = document.getElementById("senha").value;

  try{
    const res = await fetch(`${API}/login`, {
      method:"POST",
      headers:{ "Content-Type":"application/json" },
      body: JSON.stringify({ usuario, senha })
    });

    const data = await res.json();

    if(data.token){

      localStorage.setItem("token", data.token);

      // 🧠 expiração de 7 dias
      const expira = Date.now() + (7 * 24 * 60 * 60 * 1000);
      localStorage.setItem("token_expira", expira);

      mostrarSistema();
      carregarTasks();

    } else {
      alert("Login inválido");
    }

  }catch(e){
    alert("Erro ao conectar com servidor");
  }
}

/* =========================
🚪 SAIR
========================= */

function sair(){
  localStorage.removeItem("token");
  localStorage.removeItem("token_expira");
  location.reload();
}

/* =========================
👤 CADASTRO
========================= */

async function cadastrar() {

  const usuario = document.getElementById("usuario").value;
  const senha = document.getElementById("senha").value;

  if (!usuario || !senha) {
    alert("Preencha usuário e senha");
    return;
  }

  try {
    const res = await fetch(`${API}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ usuario, senha })
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      alert(data.erro || "Erro ao cadastrar");
      return;
    }

    alert("Usuário criado com sucesso!");
    entrar();

  } catch (e) {
    alert("Erro ao conectar com servidor");
  }
}

/* =========================
🚀 AUTO LOGIN
========================= */

function tokenValido(){
  const token = localStorage.getItem("token");
  const expira = localStorage.getItem("token_expira");

  if(!token || !expira) return false;

  if(Date.now() > Number(expira)) return false;

  return true;
}

window.onload = function(){

  if(tokenValido()){
    mostrarSistema();
    carregarTasks();
  } else {
    localStorage.removeItem("token");
    localStorage.removeItem("token_expira");
  }
}

/* =========================
📡 HEADERS
========================= */

function getHeaders(){
  const token = localStorage.getItem("token");

  return {
    "Content-Type":"application/json",
    "Authorization": `Bearer ${token}`
  };
}

/* =========================
📥 CARREGAR TAREFAS (CORRIGIDO)
========================= */

async function carregarTasks(){
  try{

    const token = localStorage.getItem("token");

    console.log("TOKEN:", token);

    const res = await fetch(`${API}/tarefas`, {
      method: "GET",
      headers: {
        "Content-Type":"application/json",
        "Authorization": `Bearer ${token}`
      }
    });

    console.log("STATUS:", res.status);

    const texto = await res.text();
    console.log("RESPOSTA:", texto);

    if(!res.ok){
      throw new Error("Erro HTTP " + res.status);
    }

    tasks = JSON.parse(texto);
    aplicarFiltroERender();

  }catch(e){
    console.error("Erro ao carregar tarefas:", e);
  }
}

/* =========================
➕ ADICIONAR TAREFA (CORRIGIDO)
========================= */

async function addTask(){

  let texto = document.getElementById("taskInput").value;
  let prioridade = document.getElementById("priority").value;
  let data = document.getElementById("date").value;
  let categoria = document.getElementById("category").value;

  if(texto === "") return;

  await fetch(`${API}/tarefas`,{
    method:"POST",
    headers: getHeaders(),
    body:JSON.stringify({
      texto: texto,
      data: data,
      categoria: categoria,
      prioridade: prioridade
    })
  });

  document.getElementById("taskInput").value = "";
  carregarTasks();
}

/* =========================
❌ EXCLUIR / ✔ CONCLUIR
========================= */

async function excluirTask(id){
  await fetch(`${API}/tarefas/${id}`,{
    method:"DELETE",
    headers: getHeaders()
  });

  carregarTasks();
}

async function concluirTask(id){
  await fetch(`${API}/tarefas/${id}`,{
    method:"PUT",
    headers: getHeaders()
  });

  carregarTasks();
}

/* =========================
🔍 FILTRO
========================= */

function filtrar(){
  filtroAtual = document.getElementById("filtroCategoria").value;
  aplicarFiltroERender();
}

function aplicarFiltroERender(){
  let lista = tasks;

  if(filtroAtual){
    lista = tasks.filter(t => t.categoria === filtroAtual);
  }

  render(lista);
}

/* =========================
🎯 RENDER + DASHBOARD
========================= */

function render(lista){

  let list = document.getElementById("taskList");
  list.innerHTML="";

  let hoje = new Date();
  hoje.setHours(0,0,0,0);

  let vencidas = 0;
  let proximas = 0;
  let concluidas = 0;

  let prioridade = { urgente:0, medio:0, nao:0 };
  let categoria = {};

  lista.forEach(task=>{

    let li=document.createElement("li");

    let dataTask = new Date(task.data);
    dataTask.setHours(0,0,0,0);

    if(task.concluida){
      li.classList.add("concluida");
      concluidas++;
    } else {
      if(dataTask < hoje){
        li.classList.add("vencida");
        vencidas++;
      } else {
        proximas++;
      }
    }

    prioridade[task.prioridade]++;

    if(!categoria[task.categoria]){
      categoria[task.categoria]=0;
    }
    categoria[task.categoria]++;

    li.innerHTML=`
      ${task.texto} - ${task.data}

      <button onclick="concluirTask(${task.id})">✔</button>
      <button onclick="excluirTask(${task.id})">🗑</button>
    `;

    list.appendChild(li);
  });

  document.getElementById("vencidos").innerText = vencidas;
  document.getElementById("proximos").innerText = proximas;
  document.getElementById("concluidos").innerText = concluidas;

  criarGraficos(prioridade, categoria);
}

/* =========================
📊 GRÁFICOS
========================= */

let grafico1, grafico2;

function criarGraficos(prioridade, categoria){

  if(grafico1) grafico1.destroy();
  if(grafico2) grafico2.destroy();

  grafico1 = new Chart(document.getElementById("graficoPrioridade"), {
    type: 'doughnut',
    data: {
      labels: ["Urgente","Médio","Não urgente"],
      datasets: [{
        data: [
          prioridade.urgente,
          prioridade.medio,
          prioridade.nao
        ]
      }]
    }
  });

  grafico2 = new Chart(document.getElementById("graficoCategoria"), {
    type: 'bar',
    data: {
      labels: Object.keys(categoria),
      datasets: [{
        label: "Tarefas",
        data: Object.values(categoria)
      }]
    }
  });
}

/* =========================
👁 MOSTRAR SISTEMA
========================= */

function mostrarSistema(){
  document.getElementById("loginBox").style.display="none";
  document.getElementById("app").style.display="block";
}
