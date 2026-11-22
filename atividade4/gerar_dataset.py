# Gera o dataset sintético de moedas no formato YOLO: cola recortes de moedas reais (moedas_base/) sobre
# fundos de mesa, com rotação, sombra, luz e tamanho variados. Como o programa sabe onde pôs cada moeda,
# as caixas e o total em reais saem exatos, sem anotação manual.
# Uso: python gerar_dataset.py   -> cria dataset/{train,valid,test}/{images,labels} e dataset/data.yaml
import glob, os, random
import cv2
import numpy as np

# Limites do enunciado: no mínimo 60 imagens (recomendado 100 ou mais), de 5 a 40 moedas por imagem,
# divididas em treino (70%), validação (20%) e teste (10%)
IMAGENS = {"train": 140, "valid": 40, "test": 20}
MIN_MOEDAS, MAX_MOEDAS = 5, 40
LARGURA, ALTURA = 1280, 960

DIAMETRO_MM = {"5c": 22, "10c": 20, "25c": 25, "50c": 23, "1real": 27}  # 2a família do real
CLASSES = [f"{v}_{f}" for v in DIAMETRO_MM for f in ["valor", "efigie"]]
RECORTES = {c: [cv2.imread(p, cv2.IMREAD_UNCHANGED) for p in sorted(glob.glob(f"moedas_base/{c}_*.png"))]
            for c in CLASSES}


def fundo():
    # mesa de madeira, papel, tecido ou cor lisa, com ruído
    y, x = np.mgrid[0:ALTURA, 0:LARGURA].astype(np.float32)
    ruido = cv2.GaussianBlur(np.random.randn(ALTURA, LARGURA).astype(np.float32), (0, 0), 2)
    tipo = random.choice(["madeira", "papel", "tecido", "liso"])
    if tipo == "madeira":
        cor = np.array([random.uniform(40, 90), random.uniform(80, 130), random.uniform(120, 190)])
        veios = np.sin((y + 25 * np.sin(x / random.uniform(80, 300))) / random.uniform(4, 12))
        fibras = cv2.GaussianBlur(np.random.randn(ALTURA, LARGURA).astype(np.float32), (0, 0), sigmaX=40, sigmaY=1)
        textura = 1 + 0.08 * veios + 0.6 * fibras + 0.03 * ruido
    elif tipo == "papel":
        cor = np.full(3, random.uniform(200, 245)) + np.random.uniform(-10, 10, 3)
        textura = 1 + 0.02 * ruido
    elif tipo == "tecido":
        cor = np.random.uniform(40, 200, 3)
        p = random.uniform(3, 6)
        textura = 1 + 0.06 * np.sin(x * 2 * np.pi / p) * np.sin(y * 2 * np.pi / p) + 0.05 * ruido
    else:
        cor = np.random.uniform(30, 220, 3)
        textura = 1 + 0.03 * ruido
    img = textura[..., None] * cor
    if random.random() < 0.5:  # veios na vertical
        img = cv2.resize(img.transpose(1, 0, 2), (LARGURA, ALTURA))
    return img


def preparar_moeda(classe, px_por_mm):
    # recorte da moeda no tamanho certo, girado, levemente achatado (câmera inclinada) e com brilho variado
    rec = random.choice(RECORTES[classe]).astype(np.float32)
    d = DIAMETRO_MM[classe.split("_")[0]] * px_por_mm * random.uniform(0.98, 1.02)
    rec = cv2.resize(rec, (int(d), int(d * random.uniform(0.93, 1.0))), interpolation=cv2.INTER_AREA)
    lado = int(d * 1.05)
    giro = cv2.getRotationMatrix2D((rec.shape[1] / 2, rec.shape[0] / 2), random.uniform(0, 360), 1)
    giro[:, 2] += [(lado - rec.shape[1]) / 2, (lado - rec.shape[0]) / 2]
    rec = cv2.warpAffine(rec, giro, (lado, lado), flags=cv2.INTER_LINEAR)
    rec[..., :3] = rec[..., :3] * random.uniform(0.8, 1.2) + random.uniform(-25, 25)
    return np.clip(rec, 0, 255)


def colar(img, rec, x, y):
    # sombra (alfa borrado e deslocado) e depois a moeda, com x, y no canto superior esquerdo
    h, w = rec.shape[:2]
    alfa = rec[..., 3:] / 255
    sombra = cv2.GaussianBlur(alfa, (0, 0), w * 0.04)[..., None]
    dx, dy = int(w * 0.05), int(w * 0.05)
    img[y + dy:y + dy + h, x + dx:x + dx + w] *= 1 - 0.5 * sombra
    img[y:y + h, x:x + w] = img[y:y + h, x:x + w] * (1 - alfa) + rec[..., :3] * alfa


def gerar_imagem():
    img = fundo()
    px_por_mm = random.uniform(3.0, 4.5)  # distância da câmera
    colocadas = []  # (classe, cx, cy, raio, caixa)
    for _ in range(random.randint(MIN_MOEDAS, MAX_MOEDAS)):
        classe = random.choice(CLASSES)
        rec = preparar_moeda(classe, px_por_mm)
        h, w = rec.shape[:2]
        r = w / 2
        for _ in range(200):  # procura um lugar livre; moedas podem encostar, mas não se cobrir
            x, y = random.randint(10, LARGURA - w - 20), random.randint(10, ALTURA - h - 20)
            cx, cy = x + w / 2, y + h / 2
            if all(np.hypot(cx - c[1], cy - c[2]) >= 0.97 * (r + c[3]) for c in colocadas):
                break
        else:
            continue  # não coube
        colar(img, rec, x, y)
        ys, xs = np.nonzero(rec[..., 3] > 127)  # caixa justa a partir da parte visível da moeda
        colocadas.append((classe, cx, cy, r, (x + xs.min(), y + ys.min(), x + xs.max(), y + ys.max())))

    # luz desigual (mais clara de um lado), ruído do sensor e desfoque leve
    y, x = np.mgrid[0:ALTURA, 0:LARGURA].astype(np.float32)
    ang = random.uniform(0, 2 * np.pi)
    grad = (x * np.cos(ang) + y * np.sin(ang)) / np.hypot(LARGURA, ALTURA)
    img *= (random.uniform(0.75, 1.1) + random.uniform(0, 0.4) * grad)[..., None]
    img += np.random.randn(*img.shape) * random.uniform(1, 5)
    img = np.clip(img, 0, 255).astype(np.uint8)
    if random.random() < 0.5:
        img = cv2.GaussianBlur(img, (0, 0), random.uniform(0.5, 1.2))
    return img, colocadas


random.seed(42)
np.random.seed(42)
for split, n in IMAGENS.items():
    os.makedirs(f"dataset/{split}/images", exist_ok=True)
    os.makedirs(f"dataset/{split}/labels", exist_ok=True)
    for i in range(n):
        img, colocadas = gerar_imagem()
        nome = f"dataset/{split}/%s/{split}_{i:03d}"
        cv2.imwrite(nome % "images" + ".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, random.randint(75, 95)])
        with open(nome % "labels" + ".txt", "w") as f:  # classe x_centro y_centro largura altura (0 a 1)
            for classe, _, _, _, (x1, y1, x2, y2) in colocadas:
                f.write(f"{CLASSES.index(classe)} {(x1 + x2) / 2 / LARGURA:.6f} {(y1 + y2) / 2 / ALTURA:.6f} "
                        f"{(x2 - x1) / LARGURA:.6f} {(y2 - y1) / ALTURA:.6f}\n")
    print(split, n, "imagens")

with open("dataset/data.yaml", "w") as f:
    f.write(f"train: train/images\nval: valid/images\ntest: test/images\nnc: {len(CLASSES)}\nnames: {CLASSES}\n")
