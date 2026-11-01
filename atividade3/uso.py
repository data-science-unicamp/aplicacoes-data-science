# Uso: python uso.py imagem1.jpg [imagem2.jpg ...]  (precisa do best.pt na mesma pasta)
import sys
from ultralytics import YOLO

model = YOLO("best.pt")
results = model.predict(sys.argv[1:], conf=0.25, save=True)

for r in results:
    for box in r.boxes:
        print(r.path, model.names[int(box.cls)], float(box.conf))
