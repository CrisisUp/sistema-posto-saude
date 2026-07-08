const PROTOCOLO_WS = window.location.protocol === "https:" ? "wss:" : "ws:";
const WS_URL = `${PROTOCOLO_WS}//${window.location.hostname}:${window.location.port}/ws/tv`;

let socket;
let historicoChamadas = [];
let ultimoPaciente = null; // ← NOVO: Guarda o paciente atual

// --- FUNÇÃO DE RENDERIZAÇÃO DO HISTÓRICO ---
function renderizarHistorico() {
  const container = document.getElementById("historicoLista");
  if (!container) return;

  container.innerHTML = "";

  historicoChamadas.forEach((paciente, index) => {
    const item = document.createElement("div");

    // Adiciona classe especial para as 2 últimas chamadas
    const isNova = index < 2;
    item.className = `historico-item ${isNova ? "nova-chamada" : ""}`;

    // Formata a hora
    const horaFormatada =
      paciente.hora ||
      new Date().toLocaleTimeString("pt-BR", {
        hour: "2-digit",
        minute: "2-digit",
      });

    item.innerHTML = `
            <div class="paciente-info">
                <span class="paciente-nome">${paciente.nome}</span>
                <span class="paciente-sala">${paciente.sala}</span>
            </div>
            <span class="chamada-hora">${horaFormatada}</span>
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
          const elementoNome = document.getElementById("nomePacienteDestaque");
          const elementoSala = document.getElementById("salaDestino");

          if (elementoNome && elementoSala) {
            const nomeFormatado = dados.nome.toUpperCase();
            const salaFormatada = dados.sala.toUpperCase();

            elementoNome.innerText = nomeFormatado;
            elementoSala.innerText = salaFormatada;
            elementoSala.style.display = "inline-block";

            // 🆕 GUARDA O PACIENTE ATUAL
            ultimoPaciente = {
              nome: nomeFormatado,
              sala: salaFormatada,
              hora: new Date().toLocaleTimeString("pt-BR", {
                hour: "2-digit",
                minute: "2-digit",
              }),
            };
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

      const elementoNome = document.getElementById("nomePacienteDestaque");
      const elementoSala = document.getElementById("salaDestino");

      if (!elementoNome || !elementoSala) {
        console.warn(
          "Elementos do painel principal não foram encontrados no HTML.",
        );
        return;
      }

      // 🆕 FORMATA OS DADOS RECEBIDOS
      const novoNome = dados.nome.toUpperCase();
      const novaSala = dados.sala.toUpperCase();

      // 🆕 SALVA O PACIENTE ATUAL NO HISTÓRICO (USANDO OS DADOS DO WEBSOCKET)
      if (ultimoPaciente && ultimoPaciente.nome !== novoNome) {
        // Se o paciente atual é diferente do novo, salva no histórico
        const agora = new Date();
        const horaFormatada = agora.toLocaleTimeString("pt-BR", {
          hour: "2-digit",
          minute: "2-digit",
        });

        // 🔥 CORREÇÃO: USA OS DADOS DO WEBSOCKET, NÃO DA TELA!
        historicoChamadas.unshift({
          nome: ultimoPaciente.nome,
          sala: ultimoPaciente.sala,
          hora: horaFormatada,
        });

        if (historicoChamadas.length > 5) {
          historicoChamadas.pop();
        }
        renderizarHistorico();
      }

      // 📺 ATUALIZA O PAINEL PRINCIPAL
      elementoNome.innerText = novoNome;
      elementoSala.innerText = novaSala;
      elementoSala.style.display = "inline-block";

      // 🆕 ATUALIZA O PACIENTE ATUAL
      ultimoPaciente = {
        nome: novoNome,
        sala: novaSala,
      };

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
    ganho1.gain.exponentialRampToValueAtTime(
      0.00001,
      audioCtx.currentTime + 0.4,
    );
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
        ganho2.gain.exponentialRampToValueAtTime(
          0.00001,
          audioCtx.currentTime + 0.5,
        );
        oscilador2.stop(audioCtx.currentTime + 0.5);
      } catch (e) {}
    }, 150);
  } catch (e) {}
}

// Inicializa o ciclo do app
conectarWebSocket();
