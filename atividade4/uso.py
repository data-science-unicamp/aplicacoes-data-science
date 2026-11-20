# Uso: python uso.py foto.jpg   (foto)  |  python uso.py   (webcam, tecla q para sair)
# Precisa do best.pt (YOLO por face, do notebook) na mesma pasta.
import sys
import cv2
from ultralytics import YOLO

VALORES = {"5c": 0.05, "10c": 0.10, "25c": 0.25, "50c": 0.50, "1real": 1.00}
CONF = 0.4  # trocar pelo conf escolhido no notebook

model = YOLO("best.pt")
fonte = sys.argv[1] if len(sys.argv) > 1 else 0

for r in model.predict(fonte, conf=CONF, imgsz=960, stream=True, verbose=False):
    # classes no formato "10c_valor" -> pega apenas "10c"
    total = sum(VALORES[model.names[int(c)].split("_")[0]] for c in r.boxes.cls)
    img = r.plot(conf=False)
    cv2.putText(img, f"Total: R$ {total:.2f}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 0, 255), 4)
    cv2.imshow("moedas", img)
    if fonte != 0:
        print(f"{len(r.boxes)} moedas | Total: R$ {total:.2f}")
    if cv2.waitKey(0 if fonte != 0 else 1) == ord("q"):
        break
cv2.destroyAllWindows()
