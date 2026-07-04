const ESPECIALIDADE_ID = 1;
const API_URL = `${window.location.protocol}//${window.location.hostname}:${window.location.port}`;
let pacienteAtual = null;

// --- DETECÇÃO DINÂMICA DO CONSULTÓRIO VIA URL ---
const parametrosUrl = new URLSearchParams(window.location.search);
const numeroSala = parametrosUrl.get("sala") || "1";
document.getElementById("tituloConsultorio").innerText =
  `Clínico Geral - Consultório ${numeroSala}`;

async function chamarProximo() {
  try {
    const respostaProximo = await fetch(
      `${API_URL}/medico/proximo/${ESPECIALIDADE_ID}`,
    );
    const paciente = await respostaProximo.json();

    if (paciente.mensagem) {
      alert("Fila vazia! Nenhum paciente aguardando nesta especialidade.");
      return;
    }

    pacienteAtual = paciente;

    // Envia a chamada passando o parâmetro correto da sala
    await fetch(`${API_URL}/medico/chamar/${paciente.id}?sala=${numeroSala}`, {
      method: "POST",
    });

    document.getElementById("nomePaciente").innerText = paciente.nome_paciente;
    document.getElementById("docPaciente").innerText =
      `CPF/SUS: ${paciente.documento_unico}`;
    document.getElementById("maePaciente").innerText =
      `Mãe: ${paciente.nome_mae}`;

    const anoNasc = new Date(paciente.data_nascimento).getFullYear();
    const anoAtual = new Date().getFullYear();
    document.getElementById("idadePaciente").innerText =
      `Idade: ${anoAtual - anoNasc} anos`;

    const badge = document.getElementById("gravidadePaciente");
    badge.className = `badge-gravidade bg-g${paciente.gravidade}`;
    badge.innerText = `Gravidade Nível ${paciente.gravidade}`;
    badge.style.display = "inline-block";

    document
      .getElementById("btnChamar")
      .classList.add("desativated" || "desativado");
    document.getElementById("btnChamar").classList.add("desativado");
    document.getElementById("btnIniciar").classList.remove("desativado");
    document.getElementById("btnAusente").classList.remove("desativado");
  } catch (erro) {
    alert("Erro de comunicação com o servidor local.");
  }
}

async function alterarStatus(acao) {
  if (!pacienteAtual) return;

  if (
    acao === "AUSENTE" &&
    !confirm(
      "Confirmar que o paciente não compareceu após as chamadas? Mandar para o fim da fila?",
    )
  ) {
    return;
  }

  try {
    const resposta = await fetch(
      `${API_URL}/medico/status/${pacienteAtual.id}?acao=${acao}`,
      { method: "POST" },
    );
    const resultado = await resposta.json();

    if (resultado.status === "sucesso") {
      if (acao === "INICIAR") {
        document.getElementById("btnIniciar").classList.add("desativado");
        document.getElementById("btnAusente").classList.add("desativado");
        document.getElementById("btnFinalizar").classList.remove("desativado");
        alert("Atendimento iniciado no consultório.");
      } else if (acao === "AUSENTE" || acao === "FINALIZAR") {
        pacienteAtual = null;
        document.getElementById("nomePaciente").innerText =
          "Nenhum paciente chamado";
        document.getElementById("docPaciente").innerText = "CPF/SUS: --";
        document.getElementById("maePaciente").innerText = "Mãe: --";
        document.getElementById("idadePaciente").innerText = "Idade: --";
        document.getElementById("gravidadePaciente").style.display = "none";

        document.getElementById("btnChamar").classList.remove("desativado");
        document.getElementById("btnIniciar").classList.add("desativado");
        document.getElementById("btnAusente").classList.add("desativado");
        document.getElementById("btnFinalizar").classList.add("desativado");

        if (acao === "FINALIZAR") alert("Atendimento finalizado com sucesso!");
        if (acao === "AUSENTE")
          alert("Paciente marcado como ausente e enviado para o fim da fila!");
      }
    } else {
      alert("Erro ao atualizar status no servidor.");
    }
  } catch (erro) {
    alert("Erro de comunicação com o servidor.");
  }
}
