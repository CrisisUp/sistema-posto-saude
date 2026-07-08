// ======================================================================
// CONFIGURAÇÃO INICIAL
// ======================================================================
const ESPECIALIDADE_ID = 1;
const API_URL = `${window.location.protocol}//${window.location.hostname}:${window.location.port}`;
let pacienteAtual = null;

// 🔥 CAPTURA A SALA DA URL (UMA ÚNICA VEZ!)
const urlParams = new URLSearchParams(window.location.search);
const numeroSala = urlParams.get("sala") || "1";

console.log("📱 SALA DO CELULAR:", numeroSala);
console.log("📱 URL COMPLETA:", window.location.href);

// ======================================================================
// INICIALIZAÇÃO DA PÁGINA
// ======================================================================
window.addEventListener("DOMContentLoaded", () => {
  const titulo = document.getElementById("tituloConsultorio");
  if (titulo) {
    titulo.innerText = `Clínico Geral - Consultório ${numeroSala}`;
  }
  atualizarListaFilaEspera();
});

// ======================================================================
// FUNÇÃO: CHAMAR PRÓXIMO PACIENTE
// ======================================================================
async function chamarProximo() {
  try {
    console.log("🔴 Chamando próximo para sala:", numeroSala);

    const respostaProximo = await fetch(
      `${API_URL}/medico/proximo/${ESPECIALIDADE_ID}`,
    );
    const paciente = await respostaProximo.json();

    if (paciente.mensagem || !paciente.id) {
      alert("Fila vazia! Nenhum paciente aguardando nesta especialidade.");
      return;
    }

    pacienteAtual = paciente;
    console.log("🟢 Paciente encontrado:", paciente.nome_paciente);

    // Envia a chamada com a sala correta
    const respostaChamar = await fetch(
      `${API_URL}/medico/chamar/${paciente.id}?sala=${numeroSala}`,
      { method: "POST" },
    );

    const resultado = await respostaChamar.json();
    console.log("📤 Resposta da chamada:", resultado);

    // Atualiza a interface
    document.getElementById("nomePaciente").innerText = paciente.nome_paciente;
    document.getElementById("docPaciente").innerText =
      `CPF/SUS: ${paciente.documento_unico}`;
    document.getElementById("maePaciente").innerText =
      `Mãe: ${paciente.nome_mae}`;

    const anoNasc = new Date(paciente.data_nascimento).getFullYear();
    const anoAtual = new Date().getFullYear();
    document.getElementById("idadePaciente").innerText =
      `Idade: ${anoAtual - anoNasc} anos`;

    // Badge de gravidade
    let badge = document.getElementById("gravidadePaciente");
    if (!badge) {
      badge = document.createElement("span");
      badge.id = "gravidadePaciente";
      document.getElementById("idadePaciente").after(badge);
    }
    badge.className = `badge-gravidade gravidade-${paciente.gravidade}`;
    badge.innerText = `Gravidade Nível ${paciente.gravidade}`;
    badge.style.display = "inline-block";
    badge.style.marginTop = "10px";

    // Controle de botões
    ajustarBotao("btnChamar", true);
    ajustarBotao("btnIniciar", false);
    ajustarBotao("btnAusente", false);
    ajustarBotao("btnFinalizar", true);
  } catch (erro) {
    console.error("❌ Erro no fluxo chamarProximo:", erro);
    alert("Erro de comunicação com o servidor local.");
  }
}

// ======================================================================
// FUNÇÃO: ALTERAR STATUS
// ======================================================================
async function alterarStatus(acao) {
  if (!pacienteAtual) return;

  const acaoPadrao = acao === "FINALIZAR" ? "FINALIZADO" : acao;

  if (
    acaoPadrao === "AUSENTE" &&
    !confirm(
      "Confirmar que o paciente não compareceu após as chamadas? Mandar para o fim da fila?",
    )
  ) {
    return;
  }

  try {
    console.log("🔄 Alterando status para:", acaoPadrao);

    const resposta = await fetch(
      `${API_URL}/medico/status/${pacienteAtual.id}?acao=${acaoPadrao}`,
      { method: "POST" },
    );
    const resultado = await resposta.json();
    console.log("📤 Resposta do status:", resultado);

    if (resultado.status === "sucesso") {
      if (acaoPadrao === "INICIAR") {
        ajustarBotao("btnIniciar", true);
        ajustarBotao("btnAusente", true);
        ajustarBotao("btnFinalizar", false);
        alert("Atendimento iniciado no consultório.");
      } else if (acaoPadrao === "AUSENTE" || acaoPadrao === "FINALIZADO") {
        pacienteAtual = null;

        document.getElementById("nomePaciente").innerText =
          "Aguardando chamada...";
        document.getElementById("docPaciente").innerText = "CPF/SUS: --";
        document.getElementById("maePaciente").innerText = "Mãe: --";
        document.getElementById("idadePaciente").innerText = "Idade: --";

        const badge = document.getElementById("gravidadePaciente");
        if (badge) badge.style.display = "none";

        ajustarBotao("btnChamar", false);
        ajustarBotao("btnIniciar", true);
        ajustarBotao("btnAusente", true);
        ajustarBotao("btnFinalizar", true);

        if (acaoPadrao === "FINALIZADO")
          alert("Atendimento finalizado com sucesso!");
        if (acaoPadrao === "AUSENTE") alert("Paciente marcado como ausente!");

        atualizarListaFilaEspera();
      }
    } else {
      alert("Erro ao atualizar status no servidor.");
    }
  } catch (erro) {
    console.error("❌ Erro no fluxo alterarStatus:", erro);
    alert("Erro de comunicação com o servidor.");
  }
}

// ======================================================================
// FUNÇÕES AUXILIARES
// ======================================================================
function ajustarBotao(id, desabilitar) {
  const btn = document.getElementById(id);
  if (!btn) return;

  btn.disabled = desabilitar;
  if (desabilitar) {
    btn.classList.add("btn-disabled");
  } else {
    btn.classList.remove("btn-disabled");
  }
}

async function atualizarListaFilaEspera() {
  try {
    console.log("📋 Atualizando fila...");
    const resposta = await fetch(`${API_URL}/medico/fila/${ESPECIALIDADE_ID}`);
    const pacientesFila = await resposta.json();

    const container = document.getElementById("containerFila");
    if (!container) return;

    if (pacientesFila.length === 0) {
      container.innerHTML = `<div class="paciente-sub" style="text-align: center; padding: 20px;">Nenhum paciente na fila.</div>`;
      return;
    }

    container.innerHTML = pacientesFila
      .map(
        (p) => `
            <div class="fila-item">
                <div class="paciente-dados">
                    <span class="paciente-nome">${p.nome_paciente}</span>
                    <span class="paciente-sub">Doc: ${p.documento_unico}</span>
                </div>
                <span class="badge-gravidade gravidade-${p.gravidade}">Nível ${p.gravidade}</span>
            </div>
        `,
      )
      .join("");

    console.log(`📋 Fila: ${pacientesFila.length} pacientes`);
  } catch (erro) {
    console.error("❌ Erro ao atualizar lista da fila:", erro);
  }
}

// Atualiza a fila a cada 10 segundos
setInterval(atualizarListaFilaEspera, 10000);
