import os
import streamlit as st
import pandas as pd
from datetime import date, datetime

ARQUIVO_CSV = os.path.join(os.path.dirname(__file__), "pacientes.csv")

COLUNAS = ["timestamp", "nome", "data_nascimento", "idade", "sexo",
           "nome_mae", "telefone", "convenio", "prioridade", "motivo"]

def calcular_idade(nascimento):
    hoje = date.today()
    return hoje.year - nascimento.year - (
        (hoje.month, hoje.day) < (nascimento.month, nascimento.day)
    )

def carregar_pacientes():
    if os.path.exists(ARQUIVO_CSV):
        return pd.read_csv(ARQUIVO_CSV)
    return pd.DataFrame(columns=COLUNAS)

st.set_page_config(page_title="Cadastro de Pacientes", layout="centered")
st.title("Cadastro de Pacientes")

with st.form("cadastro", clear_on_submit=True):
    nome = st.text_input("Nome do paciente")
    data_nascimento = st.date_input(
        "Data de nascimento", value=None,
        min_value=date(1900, 1, 1), max_value=date.today(),
        format="DD/MM/YYYY",
    )
    sexo = st.radio("Sexo", ["Feminino", "Masculino", "Não informado"])
    nome_mae = st.text_input("Nome da mãe")
    telefone = st.text_input("Telefone", placeholder="(19) 99999-9999")
    convenio = st.selectbox(
        "Convênio",
        ["Particular", "Unimed", "Bradesco Saúde", "SulAmérica", "Outro"],
    )
    prioridade = st.slider("Prioridade do atendimento", 1, 5)
    motivo = st.text_area("Motivo da consulta / observações")
    enviado = st.form_submit_button("Cadastrar")

if enviado and data_nascimento is None:
    st.error("Informe a data de nascimento.")
elif enviado:
    nova_linha = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "nome": nome,
        "data_nascimento": data_nascimento.strftime("%d/%m/%Y"),
        "idade": calcular_idade(data_nascimento),
        "sexo": sexo, "nome_mae": nome_mae, "telefone": telefone,
        "convenio": convenio, "prioridade": prioridade,
        "motivo": motivo,
    }
    novo = pd.DataFrame([nova_linha], columns=COLUNAS)
    if os.path.exists(ARQUIVO_CSV):
        novo.to_csv(ARQUIVO_CSV, mode="a", header=False, index=False)
    else:
        novo.to_csv(ARQUIVO_CSV, mode="w", header=True, index=False)
    st.success("Paciente cadastrado!")

pacientes = carregar_pacientes()

st.dataframe(pacientes.tail(10))

csv = pacientes.to_csv(index=False).encode("utf-8")

st.download_button("Baixar CSV", csv, "pacientes.csv", "text/csv")
