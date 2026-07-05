const PROTOCOLO_WS = window.location.protocol === "https:" ? "wss:" : "ws:";
const WS_URL = `${PROTOCOLO_WS}//${window.location.hostname}:${window.location.port}/ws/tv`;

let socket;
let historicoChamadas = [];

// --- FUNÇÃO DE RENDERIZAÇÃO DO HISTÓRICO ---
function renderizarHistorico() {
  // Busca o container correto configurado no HTML (historicoLista)
  const container = document.getElementById("historicoLista") || document.querySelector(".historico-lista");
  if (!container) {
    console.warn("Elemento container do histórico não foi localizado no HTML.");
    return;
  }

  // Limpa a lista anterior
  container.innerHTML = "";

  // Renderiza os últimos pacientes chamados utilizando o mesmo padrão visual elegante
  historicoChamadas.forEach((paciente) => {
    const item = document.createElement("div");
    item.className = "fila-item"; // Sincronizado com o CSS estrutural
    item.innerHTML = `
      <div class="paciente-dados">
        <span class="paciente-nome">${paciente.nome}</span>
        <span class="paciente-sub">${paciente.sala}</span>
      </div>
      <div class="paciente-dados" style="align-items: flex-end;">
        <span class="paciente-sub" style="font-weight: 600; color: var(--cor-primaria);">${paciente.hora}</span>
      </div>
    `;
    container.appendChild(item);
  });
}

function conectarWebSocket() {
  socket = new WebSocket(WS_URL);

  // --- SINCRONIZAÇÃO DE ESTADO INICIAL (ONOPEN) ---
  socket.onopen = async function () {
    console.log("Conectado ao WebSocket. Sincronizando estado atual...");
    try {
      const resposta = await fetch(
        `${window.location.protocol}//${window.location.hostname}:${window.location.port}/medico/ultima-chamada`,
      );
      if (resposta.ok) {
        const dados = await resposta.json();

        if (dados && dados.nome) {
          // 🚨 IDs CORRIGIDOS: apontando para os novos elementos do HTML
          const elementoNome = document.getElementById("nomePacienteDestaque");
          const elementoSala = document.getElementById("salaDestino");

          if (elementoNome && elementoSala) {
            elementoNome.innerText = dados.nome.toUpperCase();
            elementoSala.innerText = dados.sala.toUpperCase();
            elementoSala.style.display = "inline-block";
          }
        }
      }
    } catch (erro) {
      console.error("Falha ao recuperar última chamada do servidor:", erro);
    }
  };

  // --- TRATAMENTO DO TEMPO REAL (ONMESSAGE) ---
  socket.onmessage = function (event) {
    console.log("Chamada recebida em tempo real:", event.data);
    try {
      const dados = JSON.parse(event.data);

      // 🚨 IDs CORRIGIDOS: apontando para os novos elementos do HTML
      const elementoNome = document.getElementById("nomePacienteDestaque");
      const elementoSala = document.getElementById("salaDestino");

      if (!elementoNome || !elementoSala) {
        console.warn("Elementos do painel principal não foram encontrados no HTML.");
        return;
      }

      const nomeAtual = elementoNome.innerText.trim().toUpperCase();

      // 🔄 GESTÃO DE HISTÓRICO: Verifica o estado anterior antes de sobrescrever
      if (
        nomeAtual !== "" &&
        !nomeAtual.includes("AGUARDANDO") &&
        !nomeAtual.includes("PAINEL ATIVO") &&
        !nomeAtual.includes("NENHUM")
      ) {
        const agora = new Date();
        const horaFormatada = agora.toLocaleTimeString("pt-BR", {
          hour: "2-digit",
          minute: "2-digit",
        });

        const pacienteAntigo = {
          nome: elementoNome.innerText,
          sala: elementoSala.innerText,
          hora: horaFormatada,
        };

        // Evita duplicar o mesmo paciente seguido se o endpoint disparar duas vezes
        if (
          historicoChamadas.length === 0 ||
          historicoChamadas[0].nome !== pacienteAntigo.nome
        ) {
          historicoChamadas.unshift(pacienteAntigo);
          if (historicoChamadas.length > 5) {
            historicoChamadas.pop();
          }
          renderizarHistorico();
        }
      }

      // 📺 ATUALIZAÇÃO DO PAINEL PRINCIPAL
      elementoNome.innerText = dados.nome.toUpperCase();
      elementoSala.innerText = dados.sala.toUpperCase();
      elementoSala.style.display = "inline-block";

      // Dispara a animação css de pulso/alerta
      elementoNome.classList.add("piscar");

      try {
        tocarSomChamada();
      } catch (audioErr) {
        console.warn("Som bloqueado pelo navegador:", audioErr);
      }

      setTimeout(() => {
        elementoNome.classList.remove("piscar");
      }, 6000);
    } catch (erroGeral) {
      console.error("Erro ao processar o onmessage:", erroGeral);
    }
  };

  socket.onclose = function () {
    console.log("WebSocket desconectado. Tentando reconectar em 3 segundos...");
    setTimeout(conectarWebSocket, 3000);
  };
}

function tocarSomChamada() {
  try {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (audioCtx.state === "suspended") return;

    const oscilador1 = audioCtx.createOscillator();
    const ganho1 = audioCtx.createGain();
    oscilador1.type = "sine";
    oscilador1.frequency.setValueAtTime(523.25, audioCtx.currentTime);
    oscilador1.connect(ganho1);
    ganho1.connect(audioCtx.destination);
    oscilador1.start();
    ganho1.gain.exponentialRampToValueAtTime(0.00001, audioCtx.currentTime + 0.4);
    oscilador1.stop(audioCtx.currentTime + 0.4);

    setTimeout(() => {
      try {
        const oscilador2 = audioCtx.createOscillator();
        const ganho2 = audioCtx.createGain();
        oscilador2.type = "sine";
        oscilador2.frequency.setValueAtTime(659.25, audioCtx.currentTime);
        oscilador2.connect(ganho2);
        ganho2.connect(audioCtx.destination);
        oscilador2.start();
        ganho2.gain.exponentialRampToValueAtTime(0.00001, audioCtx.currentTime + 0.5);
        oscilador2.stop(audioCtx.currentTime + 0.5);
      } catch (e) {}
    }, 150);
  } catch (e) {}
}

// Inicializa o ciclo do app
conectarWebSocket();