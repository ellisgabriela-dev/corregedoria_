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
      mostrarSistema();
      carregarTasks();
    } else {
      alert("Login inválido");
    }

  }catch(e){
    alert("Erro ao conectar com servidor");
  }
}

function sair(){
  localStorage.removeItem("token");
  location.reload();
}

function mostrarSistema(){
  document.getElementById("loginBox").style.display="none";
  document.getElementById("app").style.display="block";
}

/* =========================
👤 CADASTRO DE USUÁRIO
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

    // 🔥 login automático após cadastro
    entrar();

  } catch (e) {
    console.error(e);
    alert("Erro ao conectar com servidor");
  }
}

/* =========================
🚀 AUTO LOGIN
========================= */

window.onload = function(){
  const token = localStorage.getItem("token");

  if(token){
    mostrarSistema();
    carregarTasks();
  }
}

/* =========================
📡 API COM TOKEN
========================= */

function getHeaders(){
  const token = localStorage.getItem("token");

  return {
    "Content-Type":"application/json",
    "Authorization": `Bearer ${token}`
  };
}

async function carregarTasks(){
  try{
    const res = await fetch(`${API}/tarefas`, {
      headers: getHeaders()
    });

    if(res.status === 401){
      sair();
      return;
    }

    tasks = await res.json();
    aplicarFiltroERender();

  }catch(e){
    alert("Erro ao carregar tarefas");
  }
}

async function addTask(){

  let text = document.getElementById("taskInput").value;
  let priority = document.getElementById("priority").value;
  let date = document.getElementById("date").value;
  let category = document.getElementById("category").value;

  if(text==="") return;

  await fetch(`${API}/tarefas`,{
    method:"POST",
    headers: getHeaders(),
    body:JSON.stringify({
      texto:text,
      data:date,
      categoria:category,
      prioridade:priority
    })
  });

  document.getElementById("taskInput").value = "";
  carregarTasks();
}

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

  let vencidas = 0;
  let proximas = 0;
  let concluidas = 0;

  let prioridade = { urgente:0, medio:0, nao:0 };
  let categoria = {};

  lista.forEach(task=>{

    let li=document.createElement("li");
    let dataTask = new Date(task.data);

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

  document.getElementById("lateCount").innerText = vencidas;
  document.getElementById("soonCount").innerText = proximas;
  document.getElementById("doneCount").innerText = concluidas;

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

function atualizarContadores(tarefas) {
  let vencidos = 0;
  let proximos = 0;
  let concluidos = 0;

  const hoje = new Date();

  tarefas.forEach(t => {
    if (t.concluida) {
      concluidos++;
      return;
    }

    const data = new Date(t.data);
    const diff = (data - hoje) / (1000 * 60 * 60 * 24);

    if (diff < 0) vencidos++;
    else if (diff <= 2) proximos++;
  });

  document.getElementById("vencidos").innerText = vencidos;
  document.getElementById("proximos").innerText = proximos;
  document.getElementById("concluidos").innerText = concluidos;
}
