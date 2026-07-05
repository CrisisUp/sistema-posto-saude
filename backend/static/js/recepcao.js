// Melhora a UX mudando o exemplo de digitação dinamicamente
function ajustarPlaceholderDocumento() {
  const tipo = document.getElementById("tipo_documento").value;
  const campoDoc = document.getElementById("documento_unico");
  if (!campoDoc) return;

  if (tipo === "CPF") {
    campoDoc.placeholder = "000.000.000-00";
  } else {
    campoDoc.placeholder = "700.0000.0000.0000";
  }
}

// Intercepta o envio do formulário para disparar contra a API em Python
document
  .getElementById("formCadastro")
  .addEventListener("submit", async (e) => {
    e.preventDefault();

    const feedback = document.getElementById("mensagemFeedback");

    // 🔒 CONSTRUÇÃO DO PAYLOAD CONFORME O DTO PYDANTIC DO BACKEND
    const payload = {
      nome_paciente: document.getElementById("nome_paciente").value,
      tipo_documento: document.getElementById("tipo_documento").value,
      documento_unico: document.getElementById("documento_unico").value,
      nome_mae: document.getElementById("nome_mae").value,
      data_nascimento: document.getElementById("data_nascimento").value,
      gravidade: parseInt(document.getElementById("gravidade").value),
      especialidade_id: parseInt(
        document.getElementById("especialidade_id").value,
      ),
    };

    try {
      const resposta = await fetch("/recepcao/cadastrar", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const resultado = await resposta.json();

      if (resposta.ok) {
        feedback.className = "feedback-sucesso";
        feedback.innerText = `Sucesso: ${resultado.mensagem || "Paciente cadastrado!"}`;
        document.getElementById("formCadastro").reset();
        ajustarPlaceholderDocumento();
      } else {
        feedback.className = "feedback-erro";
        feedback.innerText = `Erro: ${resultado.detail || "Falha ao cadastrar."}`;
      }
    } catch (err) {
      console.error("Erro na requisição:", err);
      feedback.className = "feedback-erro";
      feedback.innerText = "Não foi possível conectar com o servidor do posto.";
    }
  });
