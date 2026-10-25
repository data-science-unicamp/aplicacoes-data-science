-- =====================================================================
-- TechFix Informática — Dados sintéticos para testes
--
-- Todos os nomes, e-mails, telefones e endereços são FICTÍCIOS (LGPD);
-- clientes em São Paulo/SP, celulares com DDD 11;
-- os e-mails usam domínios de exemplo. As datas são relativas ao momento
-- da execução (now()): OS abertas nos últimos 90 dias, com status
-- coerente com a idade (as mais antigas já foram entregues).
--
-- ATENÇÃO: o script APAGA todos os dados das tabelas antes de inserir
-- e reinicia a numeração de clientes e OS.
-- =====================================================================

begin;

-- Limpa as tabelas e reinicia as sequências de id
truncate aplicacoes_data_science_atividade2.ordens_servico,
         aplicacoes_data_science_atividade2.clientes
  restart identity;

-- Clientes (data de cadastro = abertura da primeira OS de cada um)
insert into aplicacoes_data_science_atividade2.clientes
  (nome, endereco, email, celular_whatsapp, data_cadastro)
values
  ('João Nascimento', 'Rua Augusta, 2910 - Consolação, São Paulo/SP', 'joao.nascimento@mail-exemplo.com', '11938206283', now() - interval '77.19 days'),
  ('Wagner Silva', 'Rua Domingos de Morais, 2512 - Vila Mariana, São Paulo/SP', 'wagner.silva@exemplo.com.br', '11908960793', now() - interval '74.33 days'),
  ('Letícia Pereira Teixeira', 'Rua Haddock Lobo, 158 - Cerqueira César, São Paulo/SP', 'leticia.teixeira@mail-exemplo.com', '11956477242', now() - interval '73.75 days'),
  ('Henrique Gomes', 'Av. Brigadeiro Faria Lima, 1951 - Pinheiros, São Paulo/SP', 'henrique.gomes@mail-exemplo.com', '11994889639', now() - interval '72.11 days'),
  ('Bruno Costa', 'Rua Augusta, 2943 - Consolação, São Paulo/SP', 'bruno.costa@mail-exemplo.com', '11981440217', now() - interval '68.32 days'),
  ('Thiago Costa', 'Rua Voluntários da Pátria, 2990 - Santana, São Paulo/SP', 'thiago.costa@email-ficticio.com', '11943431625', now() - interval '60.94 days'),
  ('Vanessa Moreira Silva', 'Rua Cardeal Arcoverde, 1032 - Pinheiros, São Paulo/SP', 'vanessa.silva@teste.net.br', '11998193283', now() - interval '59.71 days'),
  ('Gustavo Ribeiro', 'Rua Oscar Freire, 1760 - Jardim Paulista, São Paulo/SP', 'gustavo.ribeiro@mail-exemplo.com', '11985701169', now() - interval '59.17 days'),
  ('Renata Oliveira Pereira', 'Rua Haddock Lobo, 968 - Cerqueira César, São Paulo/SP', 'renata.pereira@teste.net.br', '5511987852260', now() - interval '57.49 days'),
  ('Natália Ferreira', 'Av. Paulista, 1227 - Bela Vista, São Paulo/SP', 'natalia.ferreira@email-ficticio.com', '11909577948', now() - interval '57.44 days'),
  ('Juliana Martins', 'Rua Teodoro Sampaio, 222 - Pinheiros, São Paulo/SP', 'juliana.martins@email-ficticio.com', '11988570400', now() - interval '55.91 days'),
  ('Gabriela Lima Teixeira', 'Av. Sumaré, 2418 - Perdizes, São Paulo/SP', 'gabriela.teixeira@mail-exemplo.com', '11979337987', now() - interval '55.5 days'),
  ('Ana Costa Vieira', 'Rua Domingos de Morais, 102 - Vila Mariana, São Paulo/SP', 'ana.vieira@exemplo.com.br', '11950662276', now() - interval '54.84 days'),
  ('Felipe Oliveira', 'Av. Interlagos, 656 - Interlagos, São Paulo/SP', 'felipe.oliveira@mail-exemplo.com', '11953784545', now() - interval '54.25 days'),
  ('Isabela Vieira', 'Av. Washington Luís, 909 - Campo Belo, São Paulo/SP', 'isabela.vieira@exemplo.com.br', '11942391044', now() - interval '54.07 days'),
  ('Beatriz Ribeiro Silva', 'Av. Ipiranga, 2228 - República, São Paulo/SP', 'beatriz.silva@exemplo.com.br', '11935232439', now() - interval '52.45 days'),
  ('Débora Martins', 'Av. Santo Amaro, 2098 - Brooklin, São Paulo/SP', 'debora.martins@email-ficticio.com', '11938427054', now() - interval '49.77 days'),
  ('Larissa Ferreira', 'Rua Tuiuti, 269 - Tatuapé, São Paulo/SP', 'larissa.ferreira@teste.net.br', '11958188539', now() - interval '40.13 days'),
  ('Lucas Vieira', 'Av. Brigadeiro Faria Lima, 2020 - Pinheiros, São Paulo/SP', 'lucas.vieira@teste.net.br', '11917830561', now() - interval '39.93 days'),
  ('Tatiane Ferreira', 'Rua da Mooca, 1664 - Mooca, São Paulo/SP', 'tatiane.ferreira@exemplo.com.br', '11927701802', now() - interval '36.46 days'),
  ('Carla Oliveira Ferreira', 'Av. Jabaquara, 206 - Saúde, São Paulo/SP', 'carla.ferreira@teste.net.br', '11931691811', now() - interval '30.01 days'),
  ('Vinícius Pereira', 'Av. Celso Garcia, 1176 - Belém, São Paulo/SP', 'vinicius.pereira@email-ficticio.com', '11988581725', now() - interval '29.94 days'),
  ('Eduarda Teixeira', 'Av. Cruzeiro do Sul, 1772 - Canindé, São Paulo/SP', 'eduarda.teixeira@exemplo.com.br', '11953117362', now() - interval '29.64 days'),
  ('Diego Mendes', 'Av. Brigadeiro Faria Lima, 362 - Pinheiros, São Paulo/SP', 'diego.mendes@mail-exemplo.com', '11929135009', now() - interval '27.76 days'),
  ('Pedro Teixeira', 'Rua Voluntários da Pátria, 1463 - Santana, São Paulo/SP', 'pedro.teixeira@email-ficticio.com', '11973146586', now() - interval '26.29 days'),
  ('Otávio Barbosa', 'Rua Oscar Freire, 1571 - Jardim Paulista, São Paulo/SP', 'otavio.barbosa@email-ficticio.com', '11965089813', now() - interval '26.01 days'),
  ('Sabrina Ribeiro', 'Rua Vergueiro, 2611 - Liberdade, São Paulo/SP', 'sabrina.ribeiro@email-ficticio.com', '11953990505', now() - interval '22.27 days'),
  ('Marcelo Carvalho Almeida', 'Av. Jabaquara, 1038 - Saúde, São Paulo/SP', 'marcelo.almeida@exemplo.com.br', '11993694466', now() - interval '21.1 days'),
  ('Rodrigo Nascimento', 'Rua Itapura, 806 - Tatuapé, São Paulo/SP', 'rodrigo.nascimento@email-ficticio.com', '11937448087', now() - interval '11.66 days'),
  ('Rafael Silva Vieira', 'Rua Cardeal Arcoverde, 1058 - Pinheiros, São Paulo/SP', 'rafael.vieira@teste.net.br', '11995270650', now() - interval '10.06 days'),
  ('Paula Santos', 'Rua Haddock Lobo, 104 - Cerqueira César, São Paulo/SP', 'paula.santos@mail-exemplo.com', '11911210435', now() - interval '9.96 days'),
  ('Mariana Vieira', 'Rua Itapura, 1799 - Tatuapé, São Paulo/SP', 'mariana.vieira@email-ficticio.com', '11903145794', now() - interval '8.71 days'),
  ('Camila Martins Ribeiro', 'Rua Pamplona, 2114 - Jardim Paulista, São Paulo/SP', 'camila.ribeiro@mail-exemplo.com', '11997171856', now() - interval '3.89 days'),
  ('Caio Costa Ferreira', 'Rua Itapura, 2408 - Tatuapé, São Paulo/SP', 'caio.ferreira@exemplo.com.br', '11972877084', now() - interval '1.9 days'),
  ('Fernando Souza', 'Rua Oscar Freire, 1761 - Jardim Paulista, São Paulo/SP', 'fernando.souza@teste.net.br', '11902997138', now() - interval '1.2 days');

-- Ordens de serviço
insert into aplicacoes_data_science_atividade2.ordens_servico
  (cliente_id, modelo_computador, problema_relatado, status, data_abertura, data_atualizacao)
values
  (1, 'PC montado Intel i5 10ª geração', 'Liga mas não dá vídeo.', 'Entregue', now() - interval '77.19 days', now() - interval '73.7 days'),
  (2, 'All-in-One Lenovo IdeaCentre 3', 'Liga mas não dá vídeo.', 'Entregue', now() - interval '74.33 days', now() - interval '61.77 days'),
  (3, 'Impressora HP DeskJet 2774', 'Erro de papel atolado mesmo sem papel.', 'Entregue', now() - interval '73.75 days', now() - interval '54.3 days'),
  (4, 'Roteador TP-Link Archer C6', 'Roteador reiniciando a cada poucos minutos.', 'Entregue', now() - interval '72.11 days', now() - interval '54.61 days'),
  (5, 'Desktop HP ProDesk 400 G7', 'Pediu upgrade para SSD e mais 8 GB de memória.', 'Entregue', now() - interval '68.32 days', now() - interval '52.5 days'),
  (6, 'MacBook Air M1', 'Dobradiça quebrada, tela solta.', 'Entregue', now() - interval '60.94 days', now() - interval '54.83 days'),
  (7, 'Notebook Acer Aspire 5', 'Tela com listras verticais coloridas.', 'Entregue', now() - interval '59.71 days', now() - interval '49.43 days'),
  (8, 'Notebook Lenovo ThinkPad E14', 'Não liga, LED de carga não acende.', 'Entregue', now() - interval '59.17 days', now() - interval '49.3 days'),
  (9, 'Notebook Acer Nitro 5', 'Superaquecendo e desligando sozinho durante jogos.', 'Concluído', now() - interval '57.49 days', now() - interval '46.41 days'),
  (10, 'Notebook Samsung Galaxy Book2', 'Muito lento, demora mais de 5 minutos para iniciar o Windows.', 'Aguardando peça', now() - interval '57.44 days', now() - interval '43.84 days'),
  (9, 'Notebook Acer Nitro 5', 'Não liga, LED de carga não acende.', 'Entregue', now() - interval '56.4 days', now() - interval '40.83 days'),
  (11, 'Desktop HP ProDesk 400 G7', 'HD com barulho de clique e arquivos corrompidos; cliente quer backup.', 'Entregue', now() - interval '55.91 days', now() - interval '52.0 days'),
  (12, 'Desktop HP ProDesk 400 G7', 'Não reconhece pendrive nas portas USB frontais.', 'Entregue', now() - interval '55.5 days', now() - interval '43.18 days'),
  (5, 'PC Gamer Ryzen 5 + RTX 3060', 'Reinicia sozinho várias vezes ao dia.', 'Entregue', now() - interval '55.3 days', now() - interval '54.08 days'),
  (13, 'Nobreak SMS Station 1200VA', 'Nobreak apitando e não segura a carga.', 'Entregue', now() - interval '54.84 days', now() - interval '41.16 days'),
  (14, 'Notebook Dell Inspiron 15 3520', 'Dobradiça quebrada, tela solta.', 'Entregue', now() - interval '54.25 days', now() - interval '49.1 days'),
  (15, 'Desktop HP ProDesk 400 G7', 'HD com barulho de clique e arquivos corrompidos; cliente quer backup.', 'Entregue', now() - interval '54.07 days', now() - interval '34.12 days'),
  (16, 'Notebook Lenovo IdeaPad 3', 'Bateria não segura carga, desliga ao tirar da tomada.', 'Entregue', now() - interval '52.45 days', now() - interval '41.37 days'),
  (17, 'All-in-One Lenovo IdeaCentre 3', 'Liga mas não dá vídeo.', 'Entregue', now() - interval '49.77 days', now() - interval '37.12 days'),
  (15, 'Notebook Positivo Motion', 'Muito lento, demora mais de 5 minutos para iniciar o Windows.', 'Entregue', now() - interval '48.92 days', now() - interval '31.32 days'),
  (8, 'PC montado Intel i5 10ª geração', 'Liga mas não dá vídeo.', 'Concluído', now() - interval '41.75 days', now() - interval '32.25 days'),
  (13, 'Notebook Acer Nitro 5', 'Dobradiça quebrada, tela solta.', 'Concluído', now() - interval '40.84 days', now() - interval '28.84 days'),
  (10, 'Impressora HP DeskJet 2774', 'Impressora puxa várias folhas de uma vez.', 'Entregue', now() - interval '40.58 days', now() - interval '33.33 days'),
  (18, 'Roteador TP-Link Archer C6', 'Roteador reiniciando a cada poucos minutos.', 'Concluído', now() - interval '40.13 days', now() - interval '35.93 days'),
  (19, 'Monitor LG 24MK430H', 'Imagem com manchas escuras no canto.', 'Entregue', now() - interval '39.93 days', now() - interval '29.16 days'),
  (2, 'Roteador TP-Link Archer C6', 'Roteador reiniciando a cada poucos minutos.', 'Entregue', now() - interval '38.3 days', now() - interval '32.46 days'),
  (3, 'Notebook Acer Nitro 5', 'Não liga, LED de carga não acende.', 'Entregue', now() - interval '36.9 days', now() - interval '35.76 days'),
  (13, 'Notebook Acer Aspire 5', 'Não liga, LED de carga não acende.', 'Aguardando peça', now() - interval '36.62 days', now() - interval '28.02 days'),
  (20, 'MacBook Air M1', 'Tela com listras verticais coloridas.', 'Concluído', now() - interval '36.46 days', now() - interval '33.7 days'),
  (12, 'Desktop Positivo Master D610', 'Infectado por vírus, abrindo propagandas no navegador.', 'Entregue', now() - interval '36.41 days', now() - interval '25.3 days'),
  (21, 'Notebook Lenovo IdeaPad 3', 'Muito lento, demora mais de 5 minutos para iniciar o Windows.', 'Concluído', now() - interval '30.01 days', now() - interval '14.4 days'),
  (22, 'Desktop Dell OptiPlex 3080', 'Fonte queimou após queda de energia.', 'Entregue', now() - interval '29.94 days', now() - interval '13.59 days'),
  (23, 'Notebook Positivo Motion', 'Superaquecendo e desligando sozinho durante jogos.', 'Entregue', now() - interval '29.64 days', now() - interval '24.24 days'),
  (24, 'Notebook Dell Inspiron 15 3520', 'Bateria não segura carga, desliga ao tirar da tomada.', 'Entregue', now() - interval '27.76 days', now() - interval '24.23 days'),
  (10, 'MacBook Air M1', 'Conector de carga com mau contato.', 'Entregue', now() - interval '26.89 days', now() - interval '24.78 days'),
  (25, 'Notebook Lenovo ThinkPad E14', 'Wi-Fi não encontra nenhuma rede.', 'Entregue', now() - interval '26.29 days', now() - interval '11.42 days'),
  (26, 'Desktop HP ProDesk 400 G7', 'Fonte queimou após queda de energia.', 'Entregue', now() - interval '26.01 days', now() - interval '14.83 days'),
  (23, 'Notebook HP 250 G9', 'Wi-Fi não encontra nenhuma rede.', 'Aguardando peça', now() - interval '25.73 days', now() - interval '9.36 days'),
  (27, 'Notebook Asus VivoBook 15', 'Não liga, LED de carga não acende.', 'Entregue', now() - interval '22.27 days', now() - interval '2.92 days'),
  (28, 'Desktop Dell OptiPlex 3080', 'Pediu upgrade para SSD e mais 8 GB de memória.', 'Concluído', now() - interval '21.1 days', now() - interval '2.76 days'),
  (28, 'Notebook Asus VivoBook 15', 'Muito lento, demora mais de 5 minutos para iniciar o Windows.', 'Concluído', now() - interval '18.23 days', now() - interval '9.21 days'),
  (23, 'MacBook Air M1', 'Bateria não segura carga, desliga ao tirar da tomada.', 'Concluído', now() - interval '15.67 days', now() - interval '7.51 days'),
  (18, 'Impressora Epson EcoTank L3250', 'Não conecta no Wi-Fi da casa.', 'Aguardando peça', now() - interval '13.65 days', now() - interval '2.28 days'),
  (3, 'Notebook Acer Aspire 5', 'Tela azul (BSOD) frequente com erro MEMORY_MANAGEMENT.', 'Entregue', now() - interval '12.54 days', now() - interval '3.14 days'),
  (29, 'Notebook Lenovo IdeaPad 3', 'Wi-Fi não encontra nenhuma rede.', 'Em análise', now() - interval '11.66 days', now() - interval '6.55 days'),
  (29, 'PC Gamer Ryzen 5 + RTX 3060', 'Fonte queimou após queda de energia.', 'Entregue', now() - interval '11.44 days', now() - interval '4.78 days'),
  (20, 'MacBook Air M1', 'Dobradiça quebrada, tela solta.', 'Concluído', now() - interval '11.38 days', now() - interval '5.14 days'),
  (21, 'Notebook Acer Aspire 5', 'Bateria não segura carga, desliga ao tirar da tomada.', 'Concluído', now() - interval '10.48 days', now() - interval '3.73 days'),
  (30, 'Monitor LG 24MK430H', 'Monitor não liga, só pisca a luz de standby.', 'Aguardando peça', now() - interval '10.06 days', now() - interval '2.21 days'),
  (31, 'Notebook Lenovo ThinkPad E14', 'Conector de carga com mau contato.', 'Em análise', now() - interval '9.96 days', now() - interval '2.34 days'),
  (32, 'Notebook Positivo Motion', 'Conector de carga com mau contato.', 'Em análise', now() - interval '8.71 days', now() - interval '6.83 days'),
  (33, 'Impressora HP DeskJet 2774', 'Impressora puxa várias folhas de uma vez.', 'Aberto', now() - interval '3.89 days', now() - interval '3.89 days'),
  (4, 'Notebook Acer Aspire 5', 'Bateria não segura carga, desliga ao tirar da tomada.', 'Aberto', now() - interval '3.58 days', now() - interval '3.58 days'),
  (11, 'Notebook Lenovo ThinkPad E14', 'Tela com listras verticais coloridas.', 'Em análise', now() - interval '2.1 days', now() - interval '0.27 days'),
  (34, 'Notebook Positivo Motion', 'Conector de carga com mau contato.', 'Aberto', now() - interval '1.9 days', now() - interval '1.9 days'),
  (15, 'Monitor Samsung 27" Odyssey G5', 'Monitor não liga, só pisca a luz de standby.', 'Aberto', now() - interval '1.31 days', now() - interval '1.31 days'),
  (35, 'Notebook Acer Aspire 5', 'Tela azul (BSOD) frequente com erro MEMORY_MANAGEMENT.', 'Aberto', now() - interval '1.2 days', now() - interval '1.2 days'),
  (22, 'Notebook HP 250 G9', 'Muito lento, demora mais de 5 minutos para iniciar o Windows.', 'Aberto', now() - interval '0.26 days', now() - interval '0.26 days');

commit;
