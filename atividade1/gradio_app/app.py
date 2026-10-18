import gradio as gr
import pandas as pd
import os
from datetime import date, datetime

ARQUIVO_CSV = os.path.join(os.path.dirname(__file__), "pacientes.csv")

COLUNAS = ["timestamp", "nome", "data_nascimento", "idade", "sexo",
           "nome_mae", "telefone", "convenio", "prioridade", "motivo"]

def carregar_ultimos():
    if os.path.exists(ARQUIVO_CSV):
        return pd.read_csv(ARQUIVO_CSV).tail(10)
    return pd.DataFrame(columns=COLUNAS)

def calcular_idade(nascimento):
    hoje = date.today()
    return hoje.year - nascimento.year - (
        (hoje.month, hoje.day) < (nascimento.month, nascimento.day)
    )

def cadastrar_paciente(nome, data_nascimento, sexo, nome_mae, telefone,
                       convenio, prioridade, motivo):
    if data_nascimento is None:
        return "Informe a data de nascimento.", gr.update()
    nascimento = data_nascimento.date()

    linha = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "nome": nome,
        "data_nascimento": nascimento.strftime("%d/%m/%Y"),
        "idade": calcular_idade(nascimento),
        "sexo": sexo, "nome_mae": nome_mae, "telefone": telefone,
        "convenio": convenio, "prioridade": prioridade,
        "motivo": motivo,
    }

    novo = pd.DataFrame([linha], columns=COLUNAS)

    if os.path.exists(ARQUIVO_CSV):
        novo.to_csv(ARQUIVO_CSV, mode="a", header=False, index=False)
    else:
        novo.to_csv(ARQUIVO_CSV, mode="w", header=True, index=False)

    return "Paciente cadastrado com sucesso!", carregar_ultimos()

with gr.Blocks() as demo:
    gr.Markdown("## Cadastro de Pacientes")
    nome = gr.Textbox(label="Nome do paciente")
    data_nascimento = gr.DateTime(
        label="Data de nascimento", include_time=False, type="datetime",
    )
    sexo = gr.Radio(["Feminino", "Masculino", "Não informado"], label="Sexo")
    nome_mae = gr.Textbox(label="Nome da mãe")
    telefone = gr.Textbox(label="Telefone", placeholder="(19) 99999-9999")
    convenio = gr.Dropdown(
        ["Particular", "Unimed", "Bradesco Saúde", "SulAmérica", "Outro"],
        label="Convênio",
    )
    prioridade = gr.Slider(1, 5, step=1, label="Prioridade do atendimento")
    motivo = gr.Textbox(label="Motivo da consulta / observações", lines=3)
    botao = gr.Button("Cadastrar")
    saida_msg = gr.Textbox(label="Status", interactive=False)
    tabela = gr.Dataframe(label="Últimos pacientes cadastrados")
    botao.click(
        cadastrar_paciente,
        [nome, data_nascimento, sexo, nome_mae, telefone,
         convenio, prioridade, motivo],
        [saida_msg, tabela],
    )
    demo.load(carregar_ultimos, None, tabela)

demo.launch(theme=gr.themes.Ocean())
