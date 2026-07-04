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
```

## Tecnologias Utilizadas

* **Backend: FastAPI (Python)** - Escolhido pela alta performance assíncrona, documentação automática (Swagger) e suporte nativo a WebSockets.

* **Banco de Dados: SQLite3** - Banco relacional leve integrado diretamente ao projeto, garantindo persistência sem dependências externas complexas.

* **Servidor de Rede Local: Uvicorn** - Servidor ASGI configurado para ouvir toda a interface de rede local (0.0.0.0).

* **Frontend: HTML5, CSS3 (Grid/Flexbox)** e **JavaScript Vanilla (Asynchronous Fetch API & WebSocket API)**.

## 🧠 Inteligência do Backend & Regras de Negócio

### * 1. Algoritmo de Ordenação da Fila (SQL)

A busca pelo próximo paciente realiza o cálculo dinâmico da idade em tempo real e aplica múltiplos níveis de ordenação:

```SQL
SELECT *, (strftime('%Y', 'now') - strftime('%Y', data_nascimento) >= 60) AS eh_idoso
FROM atendimentos
WHERE status = 'AGUARDANDO' AND especialidade_id = ?
ORDER BY gravidade DESC, eh_idoso DESC, criado_em ASC
LIMIT 1;
```

### * 2. Estratégia Baseada em Parâmetros de URL

Para evitar a replicação de arquivos HTML para cada consultório, a interface do médico captura os parâmetros de busca (window.location.search) de forma dinâmica. Assim, o endereço ?sala=2 altera dinamicamente o escopo da aplicação para o Consultório 2.

## 🔧 Instalação e Configuração Local

Pré-requisitos
Python 3.10 ou superior instalado.

Dispositivos (computador e celulares) conectados na mesma rede Wi-Fi para testes físicos.

### * 1. Clonar o Repositório e Configurar o Ambiente

```bash
# Clone o projeto
git clone [https://github.com/CrisisUp/sistema-posto-saude.git](https://github.com/CrisisUp/sistema-posto-saude.git)
cd sistema-posto-saude/backend

# Crie um ambiente virtual (Opcional, mas recomendado)
python3 -m venv venv
source venv/bin/activate  # No Windows use: venv\Scripts\activate
```

### * 2. Instalar as Dependências do Ecossistema

```bash
pip install fastapi "uvicorn[standard]" websockets
```

### * 3. Inicializar o Servidor na Rede Local

Para descobrir o IP do seu computador na rede local (no macOS/Linux use ifconfig ou no Windows use ipconfig). Sabendo o seu IP (ex: 192.168.1.11), inicialize o Uvicorn liberando o host:

```bash
uvicorn main:app --host 0.0.0.0 --reload
```

## 📱 Como Acessar as Telas

Com o servidor rodando, acesse os endereços abaixo a partir de qualquer dispositivo conectado ao mesmo Wi-Fi:

* Painel da TV (Sala de Espera): http://<SEU_IP_LOCAL>:8000/tela-tv
* Painel do Médico (Consultório 1): http://<SEU_IP_LOCAL>:8000/tela-medico?sala=1
* Painel do Médico (Consultório 2): http://<SEU_IP_LOCAL>:8000/tela-medico?sala=2
* Documentação Automática da API (Swagger): http://<SEU_IP_LOCAL>:8000/docs

Nota: Ao abrir a tela da TV, dê um clique em qualquer ponto da página para permitir que o navegador execute os bipes sonoros de notificação automaticamente.

## Desenvolvido por Cristiano Batista Pessoa 🚀
