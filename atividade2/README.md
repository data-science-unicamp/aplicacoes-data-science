# TechFix Informática — Atividade Aula 2

Sistema de ordens de serviço: cadastro em Gradio, painel em Streamlit e banco no Supabase (PostgreSQL).

## Estrutura

```
sql/schema.sql      # script de criação do banco
app_gradio.py       # interface de cadastro
app_streamlit.py    # painel de gerenciamento
requirements.txt    # dependências
.env.example        # nomes das variáveis, sem valores
evidencias/         # prints das telas e tabelas
```

## Configuração

1. Crie o banco executando `sql/schema.sql` no SQL Editor do Supabase.
   Opcional: execute `sql/seed.sql` para carregar dados sintéticos (35 clientes e 58 OS fictícios,
   com datas relativas ao dia da execução). **Atenção:** o seed apaga os dados existentes.
2. Em *Integrations → Data API*, adicione `aplicacoes_data_science_atividade2` aos **Exposed schemas** e salve.
3. Copie `.env.example` para `.env` e preencha:
   - `SUPABASE_URL` e `SUPABASE_KEY` (chave publishable/anon, em *Project Settings → API Keys*)
   - `SUPABASE_SCHEMA=aplicacoes_data_science_atividade2`
   - `GRADIO_SHARE=0` para rodar só localmente (padrão: gera link público)

## Execução

Com [uv](https://docs.astral.sh/uv/):

```bash
uv run app_gradio.py
uv run streamlit run app_streamlit.py
```

Ou com pip: `pip install -r requirements.txt`, depois `python app_gradio.py` e `streamlit run app_streamlit.py`.

- **Gradio** (http://localhost:7860): abertura de OS no balcão. Com `share` ligado, imprime um link `gradio.live` para abrir no celular.
- **Streamlit** (http://localhost:8501): painel do gerente com abas Consultar (filtros na barra lateral e exportação CSV), Cadastrar, Editar/Excluir (com confirmação) e Indicadores.

O Streamlit lê as credenciais de `.streamlit/secrets.toml`, se existir, ou do `.env`.
