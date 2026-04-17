const API = "https://agenda-api-9z5t.onrender.com";

let tasks = [];
let usuarioLogado = null;

/* ========================= */
/* 🔐 LOGIN */
/* ========================= */

async function entrar(){
  let usuario = document.getElementById("usuario").value;
  let senha = document.getElementById("senha").value;

  try{
    const res = await fetch(`${API}/login`,{
      method:"POST",
      headers:{ "Content-Type":"application/json" },
      body:JSON.stringify({ usuario, senha })
    });

    if(res.ok){
      usuarioLogado = await res.json();

      localStorage.setItem("usuario", JSON.stringify(usuarioLogado));

      mostrarSistema();
      carregarTasks();
    }else{
      alert("Login inválido");
    }

  }catch(error){
    console.error("Erro no login:", error);
  }
}

/* ========================= */
/* 👤 CADASTRO */
/* ========================= */

async function cadastrar(){
  let usuario = document.getElementById("usuario").value;
  let senha = document.getElementById("senha").value;

  try{
    const res = await fetch(`${API}/register`,{
      method:"POST",
      headers:{ "Content-Type":"application/json" },
      body:JSON.stringify({ usuario, senha })
    });

    if(res.ok){
      alert("Usuário criado! Agora faça login.");
    }else{
      alert("Usuário já existe");
    }

  }catch(error){
    console.error("Erro no cadastro:", error);
  }
}

/* ========================= */
/* 🚪 LOGOUT */
/* ========================= */

function sair(){
  localStorage.removeItem("usuario");
  location.reload();
}

/* ========================= */
/* 📺 UI */
/* ========================= */

function mostrarSistema(){
  document.getElementById("loginBox").style.display="none";
  document.getElementById("app").style.display="block";
}

/* ========================= */
/* 📡 API */
/* ========================= */

async function carregarTasks(){
  try{
    const res = await fetch(`${API}/tarefas/${usuarioLogado.id}`);
    tasks = await res.json();
    render();
  }catch(error){
    console.error("Erro ao carregar tarefas:", error);
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
    headers:{ "Content-Type":"application/json" },
    body:JSON.stringify({
      texto:text,
      data:date,
      categoria:category,
      prioridade:priority,
      usuario_id: usuarioLogado.id
    })
  });

  document.getElementById("taskInput").value = "";
  document.getElementById("date").value = "";

  carregarTasks();
}

async function excluirTask(id){
  await fetch(`${API}/tarefas/${id}`,{
    method:"DELETE"
  });

  carregarTasks();
}

async function concluirTask(id){
  await fetch(`${API}/tarefas/${id}`,{
    method:"PUT"
  });

  carregarTasks();
}

/* ========================= */
/* 🎨 RENDER */
/* ========================= */

function render(){
  let list = document.getElementById("taskList");
  list.innerHTML="";

  tasks.forEach(task=>{

    let li=document.createElement("li");

    if(task.concluida){
      li.style.textDecoration="line-through";
    }

    li.innerHTML=`
      ${task.texto} - ${task.data}

      <button onclick="concluirTask(${task.id})">✔</button>
      <button onclick="excluirTask(${task.id})">🗑</button>
    `;

    list.appendChild(li);
  });
}

/* ========================= */
/* 🚀 AUTO LOGIN */
/* ========================= */

window.onload = () => {

  const user = localStorage.getItem("usuario");

  if(user){
    usuarioLogado = JSON.parse(user);
    mostrarSistema();
    carregarTasks();
  }

};
