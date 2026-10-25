import os
import re

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from postgrest.exceptions import APIError
from supabase import ClientOptions, create_client

STATUS = ["Aberto", "Em análise", "Aguardando peça", "Concluído", "Entregue"]

# Mesmas regras dos CHECKs de sql/schema.sql
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
CELULAR_RE = re.compile(r"^[0-9]{10,13}$")

st.set_page_config(page_title="TechFix — Painel", page_icon="🛠️", layout="wide")


# ---------------------------------------------------------------------
# Conexão: credenciais de .streamlit/secrets.toml ou do ambiente/.env
# ---------------------------------------------------------------------
def credencial(nome):
    try:
        if nome in st.secrets:
            return st.secrets[nome]
    except Exception:
        pass  # sem secrets.toml: usa as variáveis de ambiente
    return os.environ[nome]


@st.cache_resource
def conectar():
    load_dotenv()
    return create_client(
        credencial("SUPABASE_URL"),
        credencial("SUPABASE_KEY"),
        options=ClientOptions(schema=credencial("SUPABASE_SCHEMA")),
    )


def mensagem_erro(erro):
    if isinstance(erro, APIError):
        if erro.code == "23505":
            return "Já existe um cliente com este e-mail."
        if erro.code == "23514":
            return "Algum campo está em formato inválido (e-mail, celular ou status)."
        return f"O banco recusou a operação: {erro.message}"
    return "Não foi possível conectar ao banco de dados. Verifique a internet e tente novamente."


def executar(operacao, sucesso):
    """Executa uma escrita no banco; em caso de sucesso, recarrega os dados e avisa.
    Se a operação retornar um texto, ele substitui a mensagem de sucesso."""
    try:
        resultado = operacao()
    except Exception as erro:
        st.error(mensagem_erro(erro))
        return
    carregar_ordens.clear()
    carregar_clientes.clear()
    st.session_state["aviso"] = resultado if isinstance(resultado, str) else sucesso
    st.rerun()


def validar_cliente(nome, endereco, email, celular):
    if not all([nome, endereco, email, celular]):
        return "Preencha nome, endereço, e-mail e celular."
    if not EMAIL_RE.match(email):
        return "E-mail inválido. Use o formato nome@dominio.com."
    if not CELULAR_RE.match(celular):
        return "Celular inválido. Digite somente números, com DDD (10 a 13 dígitos)."
    return None


# ---------------------------------------------------------------------
# Leitura
# ---------------------------------------------------------------------
@st.cache_data(ttl=60)
def carregar_ordens():
    resposta = conectar().table("ordens_servico_detalhadas").select("*").order("os_id", desc=True).execute()
    df = pd.DataFrame(resposta.data)
    for coluna in ("data_abertura", "data_atualizacao"):
        if coluna in df:
            df[coluna] = pd.to_datetime(df[coluna]).dt.tz_convert("America/Sao_Paulo").dt.tz_localize(None)
    return df


@st.cache_data(ttl=60)
def carregar_clientes():
    resposta = conectar().table("clientes").select("*").order("nome").execute()
    return pd.DataFrame(resposta.data)


st.title("🛠️ TechFix Informática — Painel de Ordens de Serviço")

try:
    ordens = carregar_ordens()
    clientes = carregar_clientes()
except Exception as erro:
    st.error(mensagem_erro(erro))
    st.stop()

if aviso := st.session_state.pop("aviso", None):
    st.success(aviso)

# ---------------------------------------------------------------------
# Filtros (barra lateral)
# ---------------------------------------------------------------------
with st.sidebar:
    st.header("Filtros")
    filtro_nome = st.text_input("Nome do cliente", placeholder="Parte do nome")
    filtro_email = st.text_input("E-mail", placeholder="Parte do e-mail")
    filtro_status = st.multiselect("Status", STATUS, placeholder="Todos")
    if st.button("Recarregar dados", width="stretch"):
        carregar_ordens.clear()
        carregar_clientes.clear()
        st.rerun()

filtradas = ordens
if not ordens.empty:
    if filtro_nome:
        filtradas = filtradas[filtradas["nome"].str.contains(filtro_nome, case=False, regex=False)]
    if filtro_email:
        filtradas = filtradas[filtradas["email"].str.contains(filtro_email, case=False, regex=False)]
    if filtro_status:
        filtradas = filtradas[filtradas["status"].isin(filtro_status)]

aba_consultar, aba_cadastrar, aba_editar, aba_indicadores = st.tabs(
    ["🔎 Consultar", "➕ Cadastrar", "✏️ Editar/Excluir", "📊 Indicadores"]
)

# ---------------------------------------------------------------------
# Consultar
# ---------------------------------------------------------------------
with aba_consultar:
    st.caption(f"{len(filtradas)} de {len(ordens)} ordens de serviço (use os filtros na barra lateral).")
    if filtradas.empty:
        st.info("Nenhuma ordem de serviço encontrada.")
    else:
        tabela = filtradas[[
            "os_id", "status", "nome", "email", "celular_whatsapp", "endereco",
            "modelo_computador", "problema_relatado", "data_abertura", "data_atualizacao",
        ]].rename(columns={
            "os_id": "OS", "status": "Status", "nome": "Cliente", "email": "E-mail",
            "celular_whatsapp": "Celular", "endereco": "Endereço", "modelo_computador": "Modelo",
            "problema_relatado": "Problema", "data_abertura": "Abertura",
            "data_atualizacao": "Atualização",
        })
        st.dataframe(
            tabela,
            hide_index=True,
            width="stretch",
            column_config={
                "Abertura": st.column_config.DatetimeColumn(format="DD/MM/YYYY HH:mm"),
                "Atualização": st.column_config.DatetimeColumn(format="DD/MM/YYYY HH:mm"),
            },
        )
        st.download_button(
            "⬇️ Exportar CSV",
            tabela.to_csv(index=False, sep=";").encode("utf-8-sig"),
            file_name="ordens_servico.csv",
            mime="text/csv",
        )

# ---------------------------------------------------------------------
# Cadastrar
# ---------------------------------------------------------------------
with aba_cadastrar:
    st.subheader("Nova ordem de serviço")
    st.caption("Se o e-mail já estiver cadastrado, a OS é vinculada ao cliente existente.")
    # O formulário só é limpo após um cadastro com sucesso, para não perder
    # o que foi digitado quando a validação falha
    CAMPOS_NOVA_OS = ["nova_nome", "nova_endereco", "nova_email", "nova_celular",
                      "nova_modelo", "nova_problema", "nova_status"]
    if st.session_state.pop("limpar_nova_os", False):
        for chave in CAMPOS_NOVA_OS:
            st.session_state.pop(chave, None)
    with st.form("nova_os"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome do cliente", placeholder="Ex.: Maria da Silva", key="nova_nome")
            endereco = st.text_input("Endereço", placeholder="Rua, número, bairro, cidade", key="nova_endereco")
            email = st.text_input("E-mail", placeholder="maria@exemplo.com", key="nova_email")
            celular = st.text_input("Celular/WhatsApp", placeholder="Somente números com DDD", key="nova_celular")
        with col2:
            modelo = st.text_input("Modelo do computador", placeholder="Ex.: Notebook Dell Inspiron 15",
                                   key="nova_modelo")
            problema = st.text_area("Problema apresentado", height=150, key="nova_problema")
            status_inicial = st.selectbox("Status inicial", STATUS, key="nova_status")
        enviar = st.form_submit_button("Cadastrar", type="primary")

    if enviar:
        nome, endereco, modelo, problema = (v.strip() for v in (nome, endereco, modelo, problema))
        email, celular = email.strip().lower(), celular.strip()
        erro = validar_cliente(nome, endereco, email, celular)
        if not erro and not (modelo and problema):
            erro = "Preencha o modelo do computador e o problema apresentado."
        if erro:
            st.error(erro)
        else:
            def inserir_os():
                banco = conectar()
                existente = banco.table("clientes").select("id").eq("email", email).execute().data
                if existente:
                    cliente_id = existente[0]["id"]
                else:
                    cliente_id = banco.table("clientes").insert({
                        "nome": nome, "endereco": endereco,
                        "email": email, "celular_whatsapp": celular,
                    }).execute().data[0]["id"]
                os_id = banco.table("ordens_servico").insert({
                    "cliente_id": cliente_id, "modelo_computador": modelo,
                    "problema_relatado": problema, "status": status_inicial,
                }).execute().data[0]["id"]
                st.session_state["limpar_nova_os"] = True
                origem = "cliente existente" if existente else "cliente novo"
                return f"Ordem de serviço nº {os_id} cadastrada com sucesso ({origem})."

            executar(inserir_os, "Ordem de serviço cadastrada com sucesso!")

# ---------------------------------------------------------------------
# Editar / Excluir
# ---------------------------------------------------------------------
def botao_excluir(alvo, rotulo, descricao, operacao, sucesso):
    """Botão de exclusão em duas etapas: o primeiro clique pede confirmação."""
    if st.session_state.get("confirmar_exclusao") != alvo:
        if st.button(rotulo, width="stretch", key=f"excluir_{alvo}"):
            st.session_state["confirmar_exclusao"] = alvo
            st.rerun()
        return
    st.warning(f"Tem certeza que deseja excluir {descricao}? Esta ação não pode ser desfeita.")
    col_sim, col_nao = st.columns(2)
    if col_sim.button("Sim, excluir", type="primary", width="stretch", key=f"sim_{alvo}"):
        st.session_state.pop("confirmar_exclusao")
        executar(operacao, sucesso)
    if col_nao.button("Cancelar", width="stretch", key=f"nao_{alvo}"):
        st.session_state.pop("confirmar_exclusao")
        st.rerun()


with aba_editar:
    col_os, col_cliente = st.columns(2, gap="large")

    with col_os:
        st.subheader("Ordem de serviço")
        if ordens.empty:
            st.info("Nenhuma ordem de serviço cadastrada.")
        else:
            rotulos_os = {
                r.os_id: f"OS {r.os_id} — {r.nome} — {r.modelo_computador} ({r.status})"
                for r in ordens.itertuples()
            }
            os_id = st.selectbox("Selecione a OS", list(rotulos_os), format_func=rotulos_os.get)
            os_atual = ordens.set_index("os_id").loc[os_id]
            st.text(f"Problema: {os_atual['problema_relatado']}")
            novo_status = st.selectbox("Status", STATUS, index=STATUS.index(os_atual["status"]))
            if st.button("Salvar status", type="primary", width="stretch"):
                executar(
                    lambda: conectar().table("ordens_servico")
                    .update({"status": novo_status}).eq("id", int(os_id)).execute(),
                    f"Status da OS {os_id} alterado para {novo_status}.",
                )
            botao_excluir(
                f"os_{os_id}", "Excluir OS", f"a OS {os_id}",
                lambda: conectar().table("ordens_servico").delete().eq("id", int(os_id)).execute(),
                f"OS {os_id} excluída.",
            )

    with col_cliente:
        st.subheader("Cliente")
        if clientes.empty:
            st.info("Nenhum cliente cadastrado.")
        else:
            rotulos_cliente = {r.id: f"{r.nome} — {r.email}" for r in clientes.itertuples()}
            cliente_id = st.selectbox("Selecione o cliente", list(rotulos_cliente), format_func=rotulos_cliente.get)
            cliente = clientes.set_index("id").loc[cliente_id]
            with st.form(f"editar_cliente_{cliente_id}"):
                nome_ed = st.text_input("Nome", cliente["nome"])
                endereco_ed = st.text_input("Endereço", cliente["endereco"])
                email_ed = st.text_input("E-mail", cliente["email"])
                celular_ed = st.text_input("Celular/WhatsApp", cliente["celular_whatsapp"])
                salvar_cliente = st.form_submit_button("Salvar cliente", type="primary")
            if salvar_cliente:
                dados = {
                    "nome": nome_ed.strip(), "endereco": endereco_ed.strip(),
                    "email": email_ed.strip().lower(), "celular_whatsapp": celular_ed.strip(),
                }
                erro = validar_cliente(*dados.values())
                if erro:
                    st.error(erro)
                else:
                    executar(
                        lambda: conectar().table("clientes").update(dados).eq("id", int(cliente_id)).execute(),
                        f"Cliente {dados['nome']} atualizado.",
                    )
            qtd_os = int((ordens["cliente_id"] == cliente_id).sum()) if not ordens.empty else 0
            botao_excluir(
                f"cliente_{cliente_id}", "Excluir cliente",
                f"o cliente {cliente['nome']} e suas {qtd_os} ordem(ns) de serviço",
                lambda: conectar().table("clientes").delete().eq("id", int(cliente_id)).execute(),
                f"Cliente {cliente['nome']} excluído.",
            )

# ---------------------------------------------------------------------
# Indicadores
# ---------------------------------------------------------------------
with aba_indicadores:
    contagem = (
        ordens["status"].value_counts().reindex(STATUS, fill_value=0)
        if not ordens.empty else pd.Series(0, index=STATUS)
    )
    st.metric("Total de ordens de serviço", int(contagem.sum()))
    for coluna, (status, qtd) in zip(st.columns(len(STATUS)), contagem.items()):
        coluna.metric(status, int(qtd))
    st.subheader("Ordens de serviço por status")
    st.bar_chart(contagem.rename_axis("Status").rename("Quantidade"), horizontal=True, sort=False)
