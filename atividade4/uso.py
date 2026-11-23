# Soma as moedas de uma foto ou da webcam com um YOLO treinado no notebook.
# Uso: python uso.py foto.jpg   (foto)  |  python uso.py   (webcam, tecla q para sair)
# Precisa de um best.pt do notebook na mesma pasta: o de menor erro nas fotos reais é o recomendado, já que
# o uso aqui é com fotos de verdade. Funciona com o modelo por face ou por valor.
import sys
import cv2
from ultralytics import YOLO

VALORES = {"5c": 0.05, "10c": 0.10, "25c": 0.25, "50c": 0.50, "1real": 1.00}
# Limiar de confiança: abaixo dele a caixa é descartada. Trocar pelo conf escolhido no notebook para o modelo
# usado, porque foi o valor de menor erro no total na validação.
CONF = 0.4

model = YOLO("best.pt")
fonte = sys.argv[1] if len(sys.argv) > 1 else 0  # 0 é a webcam padrão

# stream=True processa um quadro por vez, sem guardar todos na memória (necessário para a webcam).
# agnostic_nms=True: no máximo uma caixa por moeda, mesmo que o modelo por face marque as duas faces.
for r in model.predict(fonte, conf=CONF, imgsz=960, agnostic_nms=True, stream=True, verbose=False):
    # Classes no formato "10c_valor" viram "10c", então o mesmo código serve para os dois modelos.
    total = sum(VALORES[model.names[int(c)].split("_")[0]] for c in r.boxes.cls)
    img = r.plot(conf=False)
    cv2.putText(img, f"Total: R$ {total:.2f}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 0, 255), 4)
    cv2.imshow("moedas", img)
    if fonte != 0:
        print(f"{len(r.boxes)} moedas | Total: R$ {total:.2f}")
    # Foto: espera uma tecla. Webcam: espera 1 ms, para o vídeo seguir, e sai com q.
    if cv2.waitKey(0 if fonte != 0 else 1) == ord("q"):
        break
cv2.destroyAllWindows()
