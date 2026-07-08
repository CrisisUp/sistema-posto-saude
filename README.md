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
SELECT *, 
       (date('now') >= date(data_nascimento, '+60 years')) AS eh_idoso
FROM atendimentos
WHERE status = 'AGUARDANDO' AND especialidade_id = ?
ORDER BY gravidade DESC, eh_idoso DESC, criado_em ASC
LIMIT 1;
```

### Tabela `atendimentos`

| Campo | Tipo | Descrição |
| ----- | ---- | --------- |
| id | INTEGER | Chave primária |
| nome_paciente | TEXT | Nome completo |
| tipo_documento | TEXT | 'CPF' ou 'SUS' |
| documento_unico | TEXT | Número criptografado |
| nome_mae | TEXT | Nome da mãe |
| data_nascimento | TEXT | Formato YYYY-MM-DD |
| gravidade | INTEGER | 1 a 5 (Manchester) |
| especialidade_id | INTEGER | FK para especialidades |
| status | TEXT | AGUARDANDO, CHAMADO, EM_ATENDIMENTO, FINALIZADO |
| criado_em | TIMESTAMP | Data/hora da chegada |
| chamado_em | TIMESTAMP | Data/hora da chamada |
| sala_atendimento | TEXT | Consultório que chamou |

### Tabela `especialidades`

| Campo | Tipo | Descrição |
| ----- | ---- | --------- |
| id | INTEGER | Chave primária |
| nome | TEXT | Nome da especialidade |
| sala | TEXT | Nome da sala/consultório |

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

### 🏥 Configuração de Salas/Consultórios

### Salas Pré-configuradas

O banco de dados já vem com 3 especialidades/salas:

| ID | Especialidade | Sala |
| -- | ------------- | ---- |
| 1 | Clínico Geral | Consultório 1 |
| 2 | Pediatria | Consultório 2 |
| 3 | Odontologia | Sala de Trauma |

### Adicionando Novas Salas

Para criar mais consultórios (ex: Consultório 3), execute no banco:

```sql
INSERT INTO especialidades (nome, sala) 
VALUES ('Ortopedia', 'Consultório 3');
```

O sistema aceita qualquer número de sala via parâmetro ?sala=X.

Se a sala existir no banco, o paciente será direcionado corretamente

Se não existir, o sistema ainda funciona, mas o paciente será chamado para o número informado

Exemplo de uso:

```text
http://192.168.1.6:8000/tela-medico?sala=3   # Consultório 3
http://192.168.1.6:8000/tela-medico?sala=10  # Consultório 10
```

### 📂 Estrutura do Projeto

```text
.
├── backend/
│   ├── app/
│   │   ├── config.py          # Configurações e chave de criptografia
│   │   ├── database.py        # Conexão com SQLite
│   │   ├── repositories.py    # Queries e acesso ao banco
│   │   ├── routes.py          # Endpoints da API
│   │   └── services.py        # Lógica de negócio (WebSocket)
│   ├── static/
│   │   ├── css/               # Estilos das telas
│   │   └── js/                # Lógica dos clientes
│   ├── templates/             # HTML das telas
│   └── main.py                # Ponto de entrada
├── banco/
│   ├── estrutura.sql          # Schema do banco
│   └── posto_saude.db         # Banco de dados SQLite
└── inserir_pacientes.py       # Script para popular dados de teste
```

### * 2. Instalar as Dependências do Ecossistema

```bash
pip install fastapi "uvicorn[standard]" websockets cryptography
```

### * 3. Inicializar o Servidor na Rede Local

Para descobrir o IP do seu computador na rede local (no macOS/Linux use ifconfig ou no Windows use `ipconfig`). Sabendo o seu IP (ex: 192.168.1.6), inicialize o Uvicorn liberando o host:

```bash
uvicorn main:app --host 0.0.0.0 --reload
```

## 📱 Como Acessar as Telas

Com o servidor rodando, acesse os endereços abaixo a partir de qualquer dispositivo conectado ao mesmo Wi-Fi:

* Painel da TV (Sala de Espera): `http://192.168.1.6:8000/tela-tv`
* Painel do Médico (Consultório 1): `http://<SEU_IP_LOCAL>:8000/tela-medico?sala=1`
* Painel do Médico (Consultório 2): `http://192.168.1.6:8000/tela-medico?sala=2`
* Tela da recepção: `http://192.168.1.6:8000/tela-recepcao`
* Documentação Automática da API (Swagger): http://<SEU_IP_LOCAL>:8000/docs

Nota: Ao abrir a tela da TV, dê um clique em qualquer ponto da página para permitir que o navegador execute os bipes sonoros de notificação automaticamente.

## 📡 Endpoints da API

| Método | Endpoint | Descrição |
| ------ | -------- | --------- |
| POST | `/recepcao/cadastrar` | Cadastra novo paciente |
| GET | `/medico/proximo/{id}` | Busca próximo paciente da fila |
| GET | `/medico/fila/{id}` | Lista todos da fila |
| POST | `/medico/chamar/{id}?sala=X` | Chama paciente para consultório |
| POST | `/medico/status/{id}?acao=X` | Altera status (INICIAR/AUSENTE/FINALIZADO) |
| GET | `/medico/ultima-chamada` | Recupera última chamada |
| WS | `/ws/tv` | WebSocket para atualização em tempo real |

## 🔐 Segurança

Os documentos dos pacientes (CPF/SUS) são **criptografados** no banco de dados usando `Fernet (symmetric encryption)`, garantindo que dados sensíveis não fiquem expostos mesmo em caso de acesso direto ao arquivo SQLite.

## Desenvolvido por Cristiano Batista Pessoa 🚀

`python inserir_pacientes.py`

* Precisa acertar a questão dos numeros das salas maiores que 2 serem aceitas (consultório 3 por exemplo)
* Melhorar o layout das últimas chamadas
