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
2. Em *Integrations → Data API*, adicione `aplicacoes_data_science_atividade2` aos **Exposed schemas** e salve.
3. Copie `.env.example` para `.env` e preencha:
   - `SUPABASE_URL` e `SUPABASE_KEY` (chave publishable/anon, em *Project Settings → API Keys*)
   - `SUPABASE_SCHEMA=aplicacoes_data_science_atividade2`
   - `GRADIO_SHARE=0` para rodar só localmente (padrão: gera link público)

## Execução

Com [uv](https://docs.astral.sh/uv/):

```bash
uv run app_gradio.py
```

Ou com pip: `pip install -r requirements.txt` e `python app_gradio.py`.

O Gradio abre em http://localhost:7860 e, com `share` ligado, imprime um link `gradio.live` para abrir no celular.
