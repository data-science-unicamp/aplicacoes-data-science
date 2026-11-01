# Atividade 3 — Detecção de objetos com YOLO11

Detector de resíduos recicláveis treinado com a biblioteca Ultralytics (`yolo11n.pt`, 50 épocas, imgsz 640)
no Google Colab com GPU T4.

- **Dataset:** [Thesis](https://universe.roboflow.com/ed-mikael-bebic-iyvku/thesis-efjq4), versão 31, de
  Ed Mikael Bebic no Roboflow Universe (licença CC BY 4.0). 4 classes (`paper`, `can`, `plastic bottle`,
  `food-wrapper`), 2.201 imagens: 1.944 de treino, 183 de validação e 74 de teste.
- **`treino.ipynb`:** treino completo e comentado, do download do dataset às evidências.
  [Abrir no Colab](https://colab.research.google.com/github/data-science-unicamp/aplicacoes-data-science/blob/main/atividade3/treino.ipynb)
- **`uso.py`:** carrega o `best.pt` e detecta objetos em imagens: `python uso.py foto.jpg`.
- `ATIVIDADE AULA 3.pdf` e `XADREZ3.ipynb`: enunciado e notebook de exemplo do professor.

A chave do Roboflow fica nos Secrets do Colab (`ROBOFLOW_API_KEY`) e não aparece no código.
