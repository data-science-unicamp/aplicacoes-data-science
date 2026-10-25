import os
import re

import gradio as gr
from dotenv import load_dotenv
from postgrest.exceptions import APIError
from supabase import ClientOptions, create_client

# Credenciais lidas do .env (nunca escritas no código)
load_dotenv()
supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"],
    options=ClientOptions(schema=os.environ["SUPABASE_SCHEMA"]),
)

# Mesmas regras dos CHECKs de sql/schema.sql
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
CELULAR_RE = re.compile(r"^[0-9]{10,13}$")


def validar(nome, endereco, email, celular, modelo, problema):
    obrigatorios = {
        "Nome do cliente": nome,
        "Endereço": endereco,
        "E-mail": email,
        "Celular/WhatsApp": celular,
        "Modelo do computador": modelo,
        "Problema apresentado": problema,
    }
    faltando = [rotulo for rotulo, valor in obrigatorios.items() if not valor]
    if faltando:
        return "Preencha os campos obrigatórios: " + ", ".join(faltando) + "."
    if not EMAIL_RE.match(email):
        return "E-mail inválido. Use o formato nome@dominio.com."
    if not CELULAR_RE.match(celular):
        return "Celular inválido. Digite somente números, com DDD (10 a 13 dígitos)."
    return None


def buscar_cliente(email):
    resposta = supabase.table("clientes").select("id, nome").eq("email", email).execute()
    return resposta.data[0] if resposta.data else None


def obter_ou_criar_cliente(nome, endereco, email, celular):
    """Reaproveita o cliente com este e-mail ou cria um novo. Retorna (cliente, criado)."""
    cliente = buscar_cliente(email)
    if cliente:
        return cliente, False
    try:
        resposta = supabase.table("clientes").insert({
            "nome": nome,
            "endereco": endereco,
            "email": email,
            "celular_whatsapp": celular,
        }).execute()
        return resposta.data[0], True
    except APIError as erro:
        # Outro atendente cadastrou o mesmo e-mail entre a busca e o insert
        if erro.code == "23505":
            return buscar_cliente(email), False
        raise


def cadastrar(nome, endereco, email, celular, modelo, problema):
    nome, endereco, modelo, problema = (v.strip() for v in (nome, endereco, modelo, problema))
    email = email.strip().lower()
    celular = celular.strip()

    erro = validar(nome, endereco, email, celular, modelo, problema)
    if erro:
        return f"❌ {erro}"

    try:
        cliente, criado = obter_ou_criar_cliente(nome, endereco, email, celular)
        resposta = supabase.table("ordens_servico").insert({
            "cliente_id": cliente["id"],
            "modelo_computador": modelo,
            "problema_relatado": problema,
            "status": "Aberto",
        }).execute()
    except APIError as erro:
        return f"❌ O banco recusou o cadastro: {erro.message}"
    except Exception:
        return "❌ Não foi possível conectar ao banco de dados. Verifique a internet e tente novamente."

    os_id = resposta.data[0]["id"]
    origem = "Cliente novo cadastrado." if criado else (
        f"E-mail já cadastrado: OS vinculada ao cliente existente ({cliente['nome']})."
    )
    return f"✅ **Ordem de serviço nº {os_id} aberta com sucesso!** Status: Aberto. {origem}"


def limpar():
    return "", "", "", "", "", "", ""


with gr.Blocks(title="TechFix — Atendimento") as demo:
    gr.Markdown(
        "# TechFix Informática — Abertura de Ordem de Serviço\n"
        "Preencha os dados do cliente e do equipamento e clique em **Cadastrar**. "
        "Se o e-mail já estiver cadastrado, a nova OS é vinculada ao cliente existente. "
        "Todos os campos são obrigatórios."
    )
    with gr.Row():
        with gr.Column(min_width=280):
            gr.Markdown("### Cliente")
            nome = gr.Textbox(label="Nome do cliente", placeholder="Ex.: Maria da Silva")
            endereco = gr.Textbox(label="Endereço", placeholder="Rua, número, bairro, cidade")
            email = gr.Textbox(label="E-mail", placeholder="maria@exemplo.com", type="email")
            celular = gr.Textbox(
                label="Celular/WhatsApp",
                placeholder="Somente números com DDD, ex.: 19999998888",
            )
        with gr.Column(min_width=280):
            gr.Markdown("### Equipamento")
            modelo = gr.Textbox(label="Modelo do computador", placeholder="Ex.: Notebook Dell Inspiron 15")
            problema = gr.Textbox(
                label="Problema apresentado",
                placeholder="Descreva o defeito relatado pelo cliente",
                lines=6,
            )
    with gr.Row():
        botao_limpar = gr.Button("Limpar")
        botao_cadastrar = gr.Button("Cadastrar", variant="primary")
    mensagem = gr.Markdown()

    campos = [nome, endereco, email, celular, modelo, problema]
    botao_cadastrar.click(cadastrar, campos, mensagem)
    botao_limpar.click(limpar, None, campos + [mensagem])

# share=True gera um link público temporário (gradio.live) para testar no celular.
# GRADIO_SHARE=0 no .env roda só localmente.
demo.launch(share=os.getenv("GRADIO_SHARE", "1") != "0", theme=gr.themes.Ocean())
