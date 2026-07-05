const ESPECIALIDADE_ID = 1;
const API_URL = `${window.location.protocol}//${window.location.hostname}:${window.location.port}`;
let pacienteAtual = null;

// Detecção dinâmica da sala via URL
const parametrosUrl = new URLSearchParams(window.location.search);
const numeroSala = parametrosUrl.get("sala") || "1";

// 🚨 CORREÇÃO: Aguarda o HTML carregar completamente antes de manipular os elementos da tela
window.addEventListener("DOMContentLoaded", () => {
  const titulo = document.getElementById("tituloConsultorio");
  if (titulo) {
    titulo.innerText = `Clínico Geral - Consultório ${numeroSala}`;
  }
  // 🚀 CHAMA AQUI PARA CARREGAR A FILA ASSIM QUE ABRIR A PÁGINA
  atualizarListaFilaEspera();
});

async function chamarProximo() {
  try {
    const respostaProximo = await fetch(
      `${API_URL}/medico/proximo/${ESPECIALIDADE_ID}`,
    );
    const paciente = await respostaProximo.json();

    if (paciente.mensagem || !paciente.id) {
      alert("Fila vazia! Nenhum paciente aguardando nesta especialidade.");
      return;
    }

    pacienteAtual = paciente;

    // Envia a chamada passando o parâmetro correto da sala para disparar o WebSocket da TV
    await fetch(`${API_URL}/medico/chamar/${paciente.id}?sala=${numeroSala}`, {
      method: "POST",
    });

    // Atualização dos dados textuais na tela
    document.getElementById("nomePaciente").innerText = paciente.nome_paciente;
    document.getElementById("docPaciente").innerText =
      `CPF/SUS: ${paciente.documento_unico}`;
    document.getElementById("maePaciente").innerText =
      `Mãe: ${paciente.nome_mae}`;

    const anoNasc = new Date(paciente.data_nascimento).getFullYear();
    const anoAtual = new Date().getFullYear();
    document.getElementById("idadePaciente").innerText =
      `Idade: ${anoAtual - anoNasc} anos`;

    // 🚨 CORREÇÃO VISUAL: Gerencia dinamicamente o badge de gravidade aplicando as cores do protocolo
    let badge = document.getElementById("gravidadePaciente");
    if (!badge) {
      // Se o badge não existir no HTML, cria ele dinamicamente abaixo da idade
      badge = document.createElement("span");
      badge.id = "gravidadePaciente";
      document.getElementById("idadePaciente").after(badge);
    }
    badge.className = `badge-gravidade gravidade-${paciente.gravidade}`;
    badge.innerText = `Gravidade Nível ${paciente.gravidade}`;
    badge.style.display = "inline-block";
    badge.style.marginTop = "10px";

    // 🔒 CONTROLE OPERACIONAL DE BOTÕES (Removendo classes antigas e aplicando o padrão .btn-disabled)
    ajustarBotao("btnChamar", true);
    ajustarBotao("btnIniciar", false);
    ajustarBotao("btnAusente", false);
    ajustarBotao("btnFinalizar", true);
  } catch (erro) {
    console.error("Erro no fluxo chamarProximo:", erro);
    alert("Erro de comunicação com o servidor local.");
  }
}

async function alterarStatus(acao) {
  if (!pacienteAtual) return;

  // Padroniza logo na entrada para evitar confusão entre FINALIZAR e FINALIZADO
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
    const resposta = await fetch(
      `${API_URL}/medico/status/${pacienteAtual.id}?acao=${acaoPadrao}`,
      { method: "POST" },
    );
    const resultado = await resposta.json();

    if (resultado.status === "sucesso") {
      if (acaoPadrao === "INICIAR") {
        ajustarBotao("btnIniciar", true);
        ajustarBotao("btnAusente", true);
        ajustarBotao("btnFinalizar", false);
        alert("Atendimento iniciado no consultório.");
      } else if (acaoPadrao === "AUSENTE" || acaoPadrao === "FINALIZADO") {
        // 🚨 CORRIGIDO: Agora valida corretamente!
        pacienteAtual = null;

        // Limpa perfeitamente o painel principal do médico
        document.getElementById("nomePaciente").innerText =
          "Aguardando chamada...";
        document.getElementById("docPaciente").innerText = "CPF/SUS: --";
        document.getElementById("maePaciente").innerText = "Mãe: --";
        document.getElementById("idadePaciente").innerText = "Idade: --";

        const badge = document.getElementById("gravidadePaciente");
        if (badge) badge.style.display = "none";

        // Devolve o controle para o botão de Chamar Próximo
        ajustarBotao("btnChamar", false);
        ajustarBotao("btnIniciar", true);
        ajustarBotao("btnAusente", true);
        ajustarBotao("btnFinalizar", true);

        if (acaoPadrao === "FINALIZADO")
          alert("Atendimento finalizado com sucesso!");
        if (acaoPadrao === "AUSENTE") alert("Paciente marcado como ausente!");

        // 🚀 REATUALIZA A COLUNA DA DIREITA APÓS MUDAR O STATUS
        atualizarListaFilaEspera();
      }
    } else {
      alert("Erro ao atualizar status no servidor.");
    }
  } catch (erro) {
    console.error("Erro no fluxo alterarStatus:", erro);
    alert("Erro de comunicação com o servidor.");
  }
}

// Helper genérico para ligar/desligar botões de forma limpa usando nosso CSS unificado
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

// Exemplo da lógica que deve rodar para alimentar aquela coluna:
async function atualizarListaFilaEspera() {
  try {
    const resposta = await fetch(`${API_URL}/medico/fila/${ESPECIALIDADE_ID}`);
    const pacientesFila = await resposta.json();

    const container = document.getElementById("containerFila");
    if (!container) return;

    if (pacientesFila.length === 0) {
      container.innerHTML = `<div class="paciente-sub" style="text-align: center; padding: 20px;">Nenhum paciente na fila.</div>`;
      return;
    }

    // Monta a lista com os badges coloridos do protocolo de Manchester
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
  } catch (erro) {
    console.error("Erro ao atualizar lista da fila:", erro);
  }
}

// Executa a busca na fila de 10 em 10 segundos para pegar novos cadastros da recepção
setInterval(atualizarListaFilaEspera, 10000);
