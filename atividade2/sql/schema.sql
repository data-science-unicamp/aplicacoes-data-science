-- =====================================================================
-- TechFix Informática — Sistema de Ordens de Serviço
-- Script de criação do banco (Supabase / PostgreSQL)
--
-- Todos os objetos ficam no schema aplicacoes_data_science_atividade2,
-- separados dos demais projetos do mesmo banco. O script pode ser
-- executado de uma vez no SQL Editor do Supabase.
-- =====================================================================


-- ---------------------------------------------------------------------
-- 1. Schema
-- Cria o schema do projeto e libera seu uso para os papéis da API do
-- Supabase (anon/authenticated = chave pública, service_role = admin).
-- Lembrete: o schema também precisa constar em
-- Project Settings → API → Exposed schemas para ser acessado via REST.
-- ---------------------------------------------------------------------
create schema if not exists aplicacoes_data_science_atividade2;

grant usage on schema aplicacoes_data_science_atividade2
  to anon, authenticated, service_role;


-- ---------------------------------------------------------------------
-- 2. Tabela clientes
-- Um registro por cliente. O e-mail é a chave natural (único) e é usado
-- pelo app Gradio para reaproveitar um cliente já cadastrado.
-- ---------------------------------------------------------------------
create table aplicacoes_data_science_atividade2.clientes (
  id               bigint generated always as identity primary key,
  nome             text        not null check (length(trim(nome)) > 0),
  endereco         text        not null check (length(trim(endereco)) > 0),
  email            text        not null unique
                   -- formato simples: algo@dominio.ext, sem espaços
                   check (email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$'),
  celular_whatsapp text        not null
                   -- somente dígitos, de 10 a 13 caracteres (DDD + número,
                   -- opcionalmente com o código do país 55)
                   check (celular_whatsapp ~ '^[0-9]{10,13}$'),
  data_cadastro    timestamptz not null default now()
);

comment on table aplicacoes_data_science_atividade2.clientes
  is 'Clientes da TechFix Informática.';


-- ---------------------------------------------------------------------
-- 3. Tabela ordens_servico
-- Cada OS pertence a um cliente; um cliente pode ter várias OS ao longo
-- do tempo (relação 1:N).
-- on delete cascade: ao excluir um cliente pelo painel (após
-- confirmação), suas ordens de serviço são excluídas junto, evitando
-- OS órfãs.
-- ---------------------------------------------------------------------
create table aplicacoes_data_science_atividade2.ordens_servico (
  id                bigint generated always as identity primary key,
  cliente_id        bigint      not null
                    references aplicacoes_data_science_atividade2.clientes (id)
                    on delete cascade,
  modelo_computador text        not null check (length(trim(modelo_computador)) > 0),
  problema_relatado text        not null check (length(trim(problema_relatado)) > 0),
  status            text        not null default 'Aberto'
                    check (status in ('Aberto', 'Em análise', 'Aguardando peça',
                                      'Concluído', 'Entregue')),
  data_abertura     timestamptz not null default now(),
  data_atualizacao  timestamptz not null default now()
);

comment on table aplicacoes_data_science_atividade2.ordens_servico
  is 'Ordens de serviço (equipamentos deixados para reparo).';


-- ---------------------------------------------------------------------
-- 4. Índices
-- A FK não cria índice automaticamente no PostgreSQL; ele acelera o join
-- com clientes e o cascade. O índice de status atende aos filtros e às
-- métricas por status do painel.
-- ---------------------------------------------------------------------
create index ordens_servico_cliente_id_idx
  on aplicacoes_data_science_atividade2.ordens_servico (cliente_id);

create index ordens_servico_status_idx
  on aplicacoes_data_science_atividade2.ordens_servico (status);


-- ---------------------------------------------------------------------
-- 5. Atualização automática de data_atualizacao
-- Trigger que grava o horário de qualquer alteração na OS (ex.: mudança
-- de status), sem depender da aplicação.
-- ---------------------------------------------------------------------
create or replace function aplicacoes_data_science_atividade2.set_data_atualizacao()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  new.data_atualizacao := now();
  return new;
end;
$$;

create trigger ordens_servico_set_data_atualizacao
  before update on aplicacoes_data_science_atividade2.ordens_servico
  for each row
  execute function aplicacoes_data_science_atividade2.set_data_atualizacao();


-- ---------------------------------------------------------------------
-- 6. View para consulta
-- Junta cada OS aos dados do cliente; é o que o painel Streamlit lista.
-- security_invoker faz a view respeitar as políticas RLS das tabelas.
-- ---------------------------------------------------------------------
create view aplicacoes_data_science_atividade2.ordens_servico_detalhadas
with (security_invoker = true) as
select
  os.id as os_id,
  os.status,
  os.modelo_computador,
  os.problema_relatado,
  os.data_abertura,
  os.data_atualizacao,
  c.id as cliente_id,
  c.nome,
  c.email,
  c.celular_whatsapp,
  c.endereco
from aplicacoes_data_science_atividade2.ordens_servico os
join aplicacoes_data_science_atividade2.clientes c on c.id = os.cliente_id;


-- ---------------------------------------------------------------------
-- 7. Permissões e políticas de acesso (RLS)
-- Os apps rodam no servidor e usam a chave anon (pública), lida do .env.
-- Com RLS ativo, nada é acessível sem política explícita; as políticas
-- abaixo liberam o CRUD completo para a chave anon, o que é adequado a
-- esta atividade com dados fictícios. Em produção, o acesso deveria
-- exigir login (papel authenticated) ou uma chave secreta no servidor.
-- ---------------------------------------------------------------------
grant select, insert, update, delete
  on all tables in schema aplicacoes_data_science_atividade2
  to anon, authenticated, service_role;

alter table aplicacoes_data_science_atividade2.clientes       enable row level security;
alter table aplicacoes_data_science_atividade2.ordens_servico enable row level security;

create policy "CRUD de clientes pelos apps"
  on aplicacoes_data_science_atividade2.clientes
  for all
  to anon, authenticated
  using (true)
  with check (true);

create policy "CRUD de ordens de servico pelos apps"
  on aplicacoes_data_science_atividade2.ordens_servico
  for all
  to anon, authenticated
  using (true)
  with check (true);
