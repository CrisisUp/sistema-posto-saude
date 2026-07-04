-- Criando a tabela de Especialidades (Fila de destino)
CREATE TABLE IF NOT EXISTS especialidades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    sala TEXT NOT NULL
);

-- Criando a tabela de Atendimentos (Dados dos pacientes e controle da fila)
CREATE TABLE IF NOT EXISTS atendimentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_paciente TEXT NOT NULL,
    documento_unico TEXT NOT NULL,       
    nome_mae TEXT NOT NULL,               
    data_nascimento TEXT NOT NULL,        
    gravidade INTEGER NOT NULL,           
    especialidade_id INTEGER NOT NULL,    
    status TEXT NOT NULL DEFAULT 'AGUARDANDO', 
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP, 
    chamado_em DATETIME,                  
    FOREIGN KEY (especialidade_id) REFERENCES especialidades(id)
);

-- Inserindo os dados iniciais das especialidades
INSERT OR IGNORE INTO especialidades (id, nome, sala) VALUES (1, 'Clínico Geral', 'Consultório 1');
INSERT OR IGNORE INTO especialidades (id, nome, sala) VALUES (2, 'Pediatria', 'Consultório 2');
INSERT OR IGNORE INTO especialidades (id, nome, sala) VALUES (3, 'Odontologia', 'Sala de Trauma');