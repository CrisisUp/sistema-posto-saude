const PROTOCOLO_WS = window.location.protocol === "https:" ? "wss:" : "ws:";
const WS_URL = `${PROTOCOLO_WS}//${window.location.hostname}:${window.location.port}/ws/tv`;

let socket;
let historicoChamadas = [];

function conectarWebSocket() {
  socket = new WebSocket(WS_URL);

  socket.onmessage = function (event) {
    const dados = JSON.parse(event.data);

    const elementoNome = document.getElementById("painelNome");
    const elementoSala = document.getElementById("painelSala");

    // Lógica do histórico com carimbo de hora
    if (elementoSala.style.display === "block") {
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

      historicoChamadas.unshift(pacienteAntigo);

      if (historicoChamadas.length > 5) {
        historicoChamadas.pop();
      }

      renderizarHistorico();
    }

    // Atualiza a chamada em destaque
    elementoNome.innerText = dados.nome.toUpperCase();
    elementoSala.innerText = dados.sala.toUpperCase();
    elementoSala.style.display = "block";

    elementoNome.classList.add("piscar");
    elementoSala.classList.add("piscar");

    tocarSomChamada();

    setTimeout(() => {
      elementoNome.classList.remove("piscar");
      elementoSala.classList.remove("piscar");
    }, 6000);
  };

  socket.onclose = function () {
    setTimeout(conectarWebSocket, 3000);
  };
}

function renderizarHistorico() {
  const listaHTML = document.getElementById("listaHistorico");
  listaHTML.innerHTML = "";

  historicoChamadas.forEach((paciente) => {
    const itemDiv = document.createElement("div");
    itemDiv.className = "historico-item";
    itemDiv.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div class="historico-nome" style="max-width: 70%;">${paciente.nome}</div>
                <span style="font-size: 13px; color: #f1c40f; font-weight: bold;">${paciente.hora}</span>
            </div>
            <div class="historico-sala">${paciente.sala}</div>
        `;
    listaHTML.appendChild(itemDiv);
  });
}

function tocarSomChamada() {
  try {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

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
    }, 150);
  } catch (e) {
    console.log("Áudio bloqueado.");
  }
}

// Inicialização automática
conectarWebSocket();
