const API = "https://SEU-SITE.onrender.com";

let tasks = [];

/* LOGIN */
function entrar(){
  let usuario = document.getElementById("usuario").value;
  let senha = document.getElementById("senha").value;

  if(usuario === "Tatiana" && senha === "1234"){
    mostrarSistema();
    carregarTasks();
  } else {
    alert("Usuário ou senha incorretos");
  }
}

function mostrarSistema(){
  document.getElementById("loginBox").style.display="none";
  document.getElementById("app").style.display="block";
}

/* API */

async function carregarTasks(){
  const res = await fetch(`${API}/tarefas`);
  tasks = await res.json();
  render();
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
      prioridade:priority
    })
  });

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

/* RENDER */

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