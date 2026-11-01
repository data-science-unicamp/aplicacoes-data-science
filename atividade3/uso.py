"""Uso do modelo treinado: detecta resíduos recicláveis (paper, can, plastic bottle, food-wrapper).

Uso: python uso.py imagem1.jpg [imagem2.jpg ...]
Precisa do best.pt na mesma pasta. As imagens com as caixas desenhadas são salvas em deteccoes/.
"""
import sys

from ultralytics import YOLO

model = YOLO("best.pt")

for imagem in sys.argv[1:]:
    results = model.predict(imagem, conf=0.25, save=True, project=".", name="deteccoes", exist_ok=True)
    print(imagem)
    for r in results:
        for box in r.boxes:
            print(f"  {model.names[int(box.cls)]}: {float(box.conf):.3f}")
