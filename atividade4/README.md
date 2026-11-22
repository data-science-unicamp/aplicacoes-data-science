# Atividade 4: contagem de moedas com YOLO11 e YOLO + ViT

Uma foto (ou a webcam) de uma mesa com moedas brasileiras vira o valor total em reais.

- **Dataset sintético:** sem moedas para fotografar, as imagens são montadas por programa.
  - `preparar_moedas.py` recorta em círculo 20 fotos reais de moedas da 2a família (2 fotos de cada face de 5c,
    10c, 25c, 50c e 1 real), do Wikimedia Commons, em domínio público ou CC0. Os recortes ficam em
    `moedas_base/`, com a fonte de cada um em `moedas_base/FONTES.md`. As fotos originais não vão para o
    repositório; para refazer os recortes, baixe-as pelos links para `originais/`.
  - `gerar_dataset.py` cola os recortes sobre fundos de mesa (madeira, papel, tecido, cor lisa), com o
    diâmetro real de cada moeda, rotação, leve inclinação, sombra, brilho, luz desigual, ruído e desfoque.
    Moedas podem encostar, mas não se cobrem. Gera 200 imagens com 5 a 40 moedas cada (140 de treino,
    40 de validação, 20 de teste) em `dataset/`, no formato YOLO, com classes por valor e face
    (`5c_valor`, `5c_efigie`, ..., `1real_efigie`). Como o programa sabe onde pôs cada moeda, as caixas e
    o total em reais são exatos.
- **Fotos reais para teste e demonstração:** 13 fotos do Brazilian Coin Detection Dataset (IEEE DataPort,
  CC BY 4.0, créditos em `reais/FONTES.md`), tiradas com celular sobre papel branco. `preparar_reais.py`
  escolhe 10 fotos de teste (`reais/teste/`, 11 a 14 moedas) e 3 de demonstração (`reais/demo/`), cada uma de
  uma sessão de fotos diferente, e converte os círculos anotados em caixas YOLO com classes por valor. Nenhuma
  foto real é usada no treino.
- **`moedas.ipynb`:** gera o dataset e faz o resto no Google Colab com GPU T4.
  [Abrir no Colab](https://colab.research.google.com/github/data-science-unicamp/aplicacoes-data-science/blob/main/atividade4/moedas.ipynb)
  - Parte A: dois `yolo11s` com fine-tuning, um com classe por valor e face e outro com classe por valor
    (`10c`), gerado a partir das mesmas caixas.
  - Parte B: o YOLO localiza, cada moeda é recortada e um ViT (`google/vit-base-patch16-224-in21k`)
    com fine-tuning classifica o recorte.
  - Avaliação: mAP, matriz de confusão, acurácia por moeda, erro médio no total em reais e tempo por imagem,
    nas 20 imagens de teste sintéticas e nas 10 fotos reais. O limiar `conf` de cada solução é escolhido pelo menor erro no total no
    conjunto de validação.
  - Análise de erros e demonstração: as 3 fotos com maior erro de cada conjunto (`erros/`) e as 3 fotos de
    demonstração (`demo/`) são salvas com as caixas, o total previsto e o total real.
- **`uso.py`:** soma as moedas de uma foto (`python uso.py foto.jpg`) ou da webcam (`python uso.py`).
- `Atividade AULA 4.pdf`: enunciado.

Limitações: treino e teste sintético vêm do mesmo gerador e dos mesmos 20 recortes, então o resultado nele tende
a ser otimista; as fotos reais medem essa diferença. Elas têm todas o mesmo fundo branco, poucas moedas por foto
(no máximo 14) e quase só moedas de 5c e 10c (no teste: 41 de 5c, 78 de 10c, 8 de 25c, 2 de 50c e nenhuma de
1 real; 2 moedas de 1 real aparecem só na demonstração).
