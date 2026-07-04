# 🏥 Sistema de Gerenciamento de Filas - Posto de Saúde

Este é um ecossistema de sistemas distribuídos projetado para otimizar o atendimento em unidades de saúde. O sistema abrange desde a recepção e triagem até o atendimento médico descentralizado e a sinalização em tempo real para os pacientes na sala de espera.

---

## 🚀 Funcionalidades Principais

* **Recepção e Triagem:** Cadastro de pacientes com classificação de risco baseada no Protocolo de Manchester (Níveis de Gravidade de 1 a 5).
* **Fila Inteligente Automatizada:** Algoritmo no banco de dados que ordena os pacientes por gravidade, aplicando prioridade legal para idosos ($\ge$ 60 anos) como critério de desempate e organizando por ordem de chegada.
* **Painel do Médico Multidispositivo:** Interface web responsiva projetada para rodar em múltiplos smartphones ou tablets na rede local simultaneamente. Cada dispositivo opera dinamicamente em uma sala/consultório diferente através de parâmetros de URL.
* **Tratamento de Ausências:** Caso um paciente não compareça à chamada, o médico pode marcá-lo como "Ausente". O sistema atualiza o timestamp e o reposiciona cirurgicamente no fim da fila de sua respectiva prioridade.
* **Painel da TV em Tempo Real:** Tela central para a sala de espera que escuta chamadas via **WebSockets**. Possui alertas visuais piscantes, histórico das últimas 5 chamadas com carimbo de hora e emissão de sinal sonoro (*beep* eletrônico) nativo.

---

## 📐 Arquitetura do Sistema

O projeto adota o modelo **Cliente-Servidor** distribuído, permitindo que múltiplos clientes consumam a mesma API centralizada na rede local:

```text
  [ Recepção (HTML/JS) ] ──(HTTP POST)──┐
                                        ▼
  [ Médico 1 (Celular) ] ──(HTTP POST)──┼─► [ Servidor FastAPI ] ──► [ Banco SQLite ]
  [ Médico 2 (Celular) ] ──(HTTP POST)──┘           │
                                              (WebSocket)
                                                    ▼
                                          [ Painel TV (Monitor) ]