# Uso: python uso.py imagem1.jpg [imagem2.jpg ...]  (precisa do best.pt na mesma pasta)
import sys
from ultralytics import YOLO

model = YOLO("best.pt")
results = model.predict(sys.argv[1:], conf=0.25, save=True, exist_ok=True)

# Cada detecção: classe, confiança e caixa (x_centro y_centro largura altura, de 0 a 1)
for r in results:
    print(r.path)
    for box in r.boxes:
        c = int(box.cls)
        xc, yc, w, h = box.xywhn[0].tolist()
        print(f"classe: {c} ({model.names[c]}) | confiança: {float(box.conf):.3f} | x_centro: {xc:.3f} | "
              f"y_centro: {yc:.3f} | largura: {w:.3f} | altura: {h:.3f}")
