# Atividade 4: contagem de moedas com YOLO11 e YOLO + ViT

Uma foto (ou a webcam) de uma mesa com moedas brasileiras vira o valor total em reais.

- **Dataset sintético:** sem moedas para fotografar, as imagens são montadas por programa.
  - `preparar_moedas.py` recorta em círculo 20 fotos reais de moedas da 2a família (2 fotos de cada face de 5c,
    10c, 25c, 50c e 1 real), do Wikimedia Commons, em domínio público ou CC0. Os recortes ficam em
    `moedas_base/`, com a fonte de cada um em `moedas_base/FONTES.md`. As fotos originais não vão para o
    repositório; para refazer os recortes, baixe-as pelos links para `originais/`.
  - `gerar_dataset.py` cola os recortes sobre fundos de mesa (madeira, papel, tecido, cor lisa), com o
    diâmetro real de cada moeda, rotação, leve inclinação, sombra, brilho, luz desigual, ruído e desfoque.
    Moedas podem encostar, mas não se cobrem. Gera 100 imagens com 5 a 40 moedas cada (70 de treino,
    20 de validação, 10 de teste) em `dataset/`, no formato YOLO, com classes por valor e face
    (`5c_valor`, `5c_efigie`, ..., `1real_efigie`). Como o programa sabe onde pôs cada moeda, as caixas e
    o total em reais são exatos.
- **`moedas.ipynb`:** gera o dataset e faz o resto no Google Colab com GPU T4.
  [Abrir no Colab](https://colab.research.google.com/github/data-science-unicamp/aplicacoes-data-science/blob/main/atividade4/moedas.ipynb)
  - Parte A: dois `yolo11s` com fine-tuning, um com classe por valor e face e outro com classe por valor
    (`10c`), gerado a partir das mesmas caixas.
  - Parte B: o YOLO localiza, cada moeda é recortada e um ViT (`google/vit-base-patch16-224-in21k`)
    com fine-tuning classifica o recorte.
  - Avaliação: mAP, matriz de confusão, acurácia por moeda, erro médio no total em reais e tempo por imagem,
    nas 10 imagens de teste. O limiar `conf` de cada solução é escolhido pelo menor erro no total no
    conjunto de validação.
- **`uso.py`:** soma as moedas de uma foto (`python uso.py foto.jpg`) ou da webcam (`python uso.py`).
- `Atividade AULA 4.pdf`: enunciado.

Limitação: treino e teste vêm do mesmo gerador e dos mesmos 20 recortes, então o resultado no teste tende a
ser otimista em relação a fotos reais de uma mesa.
