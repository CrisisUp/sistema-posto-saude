import requests
import json
import time

API_URL = "http://127.0.0.1:8000/recepcao/cadastrar"

pacientes = [
    {
        "nome_paciente": "Rodrigo Alves Gomes",
        "tipo_documento": "SUS",
        "documento_unico": "736970501590763",
        "nome_mae": "Julia Rodrigues Ferreira",
        "data_nascimento": "1987-09-17",
        "gravidade": 1,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Amanda Gomes Silva",
        "tipo_documento": "SUS",
        "documento_unico": "792839501156958",
        "nome_mae": "Larissa Pereira Santos",
        "data_nascimento": "1956-12-31",
        "gravidade": 2,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Isabela Lima Pereira",
        "tipo_documento": "SUS",
        "documento_unico": "700279788274622",
        "nome_mae": "Isabela Ribeiro Gomes",
        "data_nascimento": "1954-10-09",
        "gravidade": 1,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Camila Alves Silva",
        "tipo_documento": "SUS",
        "documento_unico": "771584351532410",
        "nome_mae": "Isabela Gomes Lopes",
        "data_nascimento": "1974-04-13",
        "gravidade": 5,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Rafael Lopes Oliveira",
        "tipo_documento": "SUS",
        "documento_unico": "714642885952508",
        "nome_mae": "Mariana Souza Martins",
        "data_nascimento": "1997-11-07",
        "gravidade": 5,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Isabela Ribeiro Martins",
        "tipo_documento": "CPF",
        "documento_unico": "43457282219",
        "nome_mae": "Julia Souza Ribeiro",
        "data_nascimento": "1991-12-26",
        "gravidade": 2,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Arthur Almeida Martins",
        "tipo_documento": "CPF",
        "documento_unico": "00439590902",
        "nome_mae": "Clara Oliveira Gomes",
        "data_nascimento": "1983-02-10",
        "gravidade": 1,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Gabriela Costa Pereira",
        "tipo_documento": "CPF",
        "documento_unico": "42208944552",
        "nome_mae": "Ana Souza Costa",
        "data_nascimento": "1953-12-15",
        "gravidade": 4,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Ana Ferreira Santos",
        "tipo_documento": "SUS",
        "documento_unico": "709962874895881",
        "nome_mae": "Ana Oliveira Souza",
        "data_nascimento": "1972-07-17",
        "gravidade": 5,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Rafael Carvalho Silva",
        "tipo_documento": "CPF",
        "documento_unico": "55325654403",
        "nome_mae": "Amanda Ferreira Silva",
        "data_nascimento": "1957-03-10",
        "gravidade": 4,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Fernanda Ferreira Carvalho",
        "tipo_documento": "SUS",
        "documento_unico": "786712765728890",
        "nome_mae": "Letícia Lima Lopes",
        "data_nascimento": "1998-01-10",
        "gravidade": 3,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Gabriela Gomes Soares",
        "tipo_documento": "SUS",
        "documento_unico": "730667199371339",
        "nome_mae": "Clara Costa Carvalho",
        "data_nascimento": "1973-01-17",
        "gravidade": 3,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Rafael Ribeiro Carvalho",
        "tipo_documento": "SUS",
        "documento_unico": "776246552318549",
        "nome_mae": "Ana Pereira Souza",
        "data_nascimento": "1990-12-13",
        "gravidade": 3,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "João Ribeiro Souza",
        "tipo_documento": "SUS",
        "documento_unico": "709155131613951",
        "nome_mae": "Letícia Silva Ribeiro",
        "data_nascimento": "2003-06-21",
        "gravidade": 4,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Guilherme Costa Silva",
        "tipo_documento": "CPF",
        "documento_unico": "88426982588",
        "nome_mae": "Amanda Gomes Santos",
        "data_nascimento": "2007-07-08",
        "gravidade": 4,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Larissa Carvalho Rodrigues",
        "tipo_documento": "SUS",
        "documento_unico": "731005873978844",
        "nome_mae": "Isabela Oliveira Santos",
        "data_nascimento": "1969-07-09",
        "gravidade": 2,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Mariana Carvalho Gomes",
        "tipo_documento": "CPF",
        "documento_unico": "58599268831",
        "nome_mae": "Julia Gomes Oliveira",
        "data_nascimento": "1969-03-14",
        "gravidade": 2,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Fernanda Lopes Alves",
        "tipo_documento": "CPF",
        "documento_unico": "50826933950",
        "nome_mae": "Clara Gomes Lopes",
        "data_nascimento": "1987-04-07",
        "gravidade": 1,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Rodrigo Souza Ferreira",
        "tipo_documento": "CPF",
        "documento_unico": "12448882012",
        "nome_mae": "Julia Lima Pereira",
        "data_nascimento": "1974-02-02",
        "gravidade": 3,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Isabela Santos Lopes",
        "tipo_documento": "SUS",
        "documento_unico": "713125763450831",
        "nome_mae": "Luana Lopes Carvalho",
        "data_nascimento": "2002-05-03",
        "gravidade": 1,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Guilherme Santos Gomes",
        "tipo_documento": "CPF",
        "documento_unico": "52496794559",
        "nome_mae": "Gabriela Ferreira Ribeiro",
        "data_nascimento": "1942-08-01",
        "gravidade": 2,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Beatriz Gomes Lopes",
        "tipo_documento": "SUS",
        "documento_unico": "720412580591032",
        "nome_mae": "Luana Silva Lopes",
        "data_nascimento": "1975-04-10",
        "gravidade": 2,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "João Almeida Soares",
        "tipo_documento": "SUS",
        "documento_unico": "737521324558542",
        "nome_mae": "Gabriela Carvalho Ferreira",
        "data_nascimento": "1970-08-01",
        "gravidade": 3,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Thiago Souza Costa",
        "tipo_documento": "CPF",
        "documento_unico": "16808203935",
        "nome_mae": "Julia Alves Alves",
        "data_nascimento": "1985-08-01",
        "gravidade": 2,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Julia Rodrigues Rodrigues",
        "tipo_documento": "CPF",
        "documento_unico": "55580799983",
        "nome_mae": "Fernanda Lopes Ribeiro",
        "data_nascimento": "2003-03-30",
        "gravidade": 5,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Rodrigo Alves Ferreira",
        "tipo_documento": "CPF",
        "documento_unico": "11833793715",
        "nome_mae": "Gabriela Santos Ferreira",
        "data_nascimento": "1997-10-06",
        "gravidade": 4,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Larissa Ribeiro Martins",
        "tipo_documento": "SUS",
        "documento_unico": "794758140007871",
        "nome_mae": "Isabela Lopes Lima",
        "data_nascimento": "1979-07-27",
        "gravidade": 4,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Amanda Oliveira Gomes",
        "tipo_documento": "CPF",
        "documento_unico": "44299718438",
        "nome_mae": "Julia Carvalho Ferreira",
        "data_nascimento": "1999-01-31",
        "gravidade": 5,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Bruno Lima Lopes",
        "tipo_documento": "CPF",
        "documento_unico": "77556619055",
        "nome_mae": "Camila Lopes Soares",
        "data_nascimento": "1982-09-15",
        "gravidade": 1,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Enzo Santos Ferreira",
        "tipo_documento": "SUS",
        "documento_unico": "717508049498103",
        "nome_mae": "Mariana Lima Rodrigues",
        "data_nascimento": "1993-09-30",
        "gravidade": 1,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Camila Soares Alves",
        "tipo_documento": "SUS",
        "documento_unico": "772016459229113",
        "nome_mae": "Letícia Ribeiro Almeida",
        "data_nascimento": "1997-11-30",
        "gravidade": 2,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Rodrigo Alves Costa",
        "tipo_documento": "CPF",
        "documento_unico": "98723854167",
        "nome_mae": "Letícia Pereira Oliveira",
        "data_nascimento": "1959-12-16",
        "gravidade": 1,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Daniel Rodrigues Souza",
        "tipo_documento": "CPF",
        "documento_unico": "31298366240",
        "nome_mae": "Laura Soares Almeida",
        "data_nascimento": "1993-06-20",
        "gravidade": 5,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Larissa Oliveira Silva",
        "tipo_documento": "CPF",
        "documento_unico": "03659802921",
        "nome_mae": "Fernanda Almeida Almeida",
        "data_nascimento": "2002-09-19",
        "gravidade": 3,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Luana Soares Souza",
        "tipo_documento": "SUS",
        "documento_unico": "713658976816914",
        "nome_mae": "Luana Gomes Lopes",
        "data_nascimento": "1994-11-29",
        "gravidade": 2,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Gabriel Martins Martins",
        "tipo_documento": "CPF",
        "documento_unico": "92234406802",
        "nome_mae": "Luana Souza Martins",
        "data_nascimento": "1976-08-16",
        "gravidade": 5,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Amanda Soares Alves",
        "tipo_documento": "CPF",
        "documento_unico": "03652583710",
        "nome_mae": "Isabela Silva Oliveira",
        "data_nascimento": "1975-05-19",
        "gravidade": 3,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Ana Carvalho Santos",
        "tipo_documento": "CPF",
        "documento_unico": "49695653617",
        "nome_mae": "Letícia Silva Martins",
        "data_nascimento": "1970-12-02",
        "gravidade": 3,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Larissa Lopes Santos",
        "tipo_documento": "SUS",
        "documento_unico": "729092192691561",
        "nome_mae": "Camila Silva Ferreira",
        "data_nascimento": "2002-01-21",
        "gravidade": 4,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Amanda Lima Lima",
        "tipo_documento": "CPF",
        "documento_unico": "36863090759",
        "nome_mae": "Ana Soares Ribeiro",
        "data_nascimento": "1991-10-29",
        "gravidade": 5,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Pedro Pereira Rodrigues",
        "tipo_documento": "SUS",
        "documento_unico": "735154842326430",
        "nome_mae": "Larissa Gomes Martins",
        "data_nascimento": "1965-10-09",
        "gravidade": 5,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Clara Carvalho Carvalho",
        "tipo_documento": "CPF",
        "documento_unico": "99672300527",
        "nome_mae": "Maria Gomes Almeida",
        "data_nascimento": "1997-02-12",
        "gravidade": 5,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Letícia Carvalho Martins",
        "tipo_documento": "CPF",
        "documento_unico": "71594897726",
        "nome_mae": "Camila Pereira Carvalho",
        "data_nascimento": "1996-12-26",
        "gravidade": 1,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Laura Silva Ferreira",
        "tipo_documento": "SUS",
        "documento_unico": "732225345833766",
        "nome_mae": "Clara Alves Oliveira",
        "data_nascimento": "2002-07-10",
        "gravidade": 1,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Daniel Gomes Oliveira",
        "tipo_documento": "CPF",
        "documento_unico": "57610792828",
        "nome_mae": "Isabela Santos Soares",
        "data_nascimento": "1998-06-19",
        "gravidade": 4,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Beatriz Ferreira Alves",
        "tipo_documento": "CPF",
        "documento_unico": "62761668767",
        "nome_mae": "Camila Lopes Alves",
        "data_nascimento": "1967-09-29",
        "gravidade": 4,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Beatriz Martins Ribeiro",
        "tipo_documento": "CPF",
        "documento_unico": "85899588859",
        "nome_mae": "Amanda Rodrigues Martins",
        "data_nascimento": "1986-05-03",
        "gravidade": 3,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Arthur Ribeiro Alves",
        "tipo_documento": "CPF",
        "documento_unico": "05735112049",
        "nome_mae": "Isabela Ribeiro Oliveira",
        "data_nascimento": "1974-05-07",
        "gravidade": 2,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Rodrigo Rodrigues Rodrigues",
        "tipo_documento": "CPF",
        "documento_unico": "17727042797",
        "nome_mae": "Mariana Almeida Souza",
        "data_nascimento": "1976-04-23",
        "gravidade": 3,
        "especialidade_id": 1
    },
    {
        "nome_paciente": "Guilherme Pereira Silva",
        "tipo_documento": "CPF",
        "documento_unico": "07191071291",
        "nome_mae": "Letícia Almeida Pereira",
        "data_nascimento": "2005-06-22",
        "gravidade": 2,
        "especialidade_id": 1
    }
]

print(f"Iniciando a carga automatizada de {len(pacientes)} pacientes via API...")

sucessos = 0
for i, p in enumerate(pacientes, 1):
    try:
        response = requests.post(API_URL, json=p)
        if response.status_code in [200, 201]:
            print(f"[{i}/50] Sucesso: {p['nome_paciente']} ({p['tipo_documento']})")
            sucessos += 1
        else:
            print(f"[{i}/50] Falha ao cadastrar {p['nome_paciente']}: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[{i}/50] Erro de conexão: {e}")
    time.sleep(0.05) # Pequena pausa para não estressar o SQLite

print(f"\nCarga finalizada! {sucessos} de {len(pacientes)} pacientes cadastrados com sucesso.")