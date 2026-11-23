# Gera o dataset sintético de moedas no formato YOLO: cola recortes de moedas reais (moedas_base/) sobre
# fundos de mesa, com rotação, sombra, luz e tamanho variados. Como o programa sabe onde pôs cada moeda,
# as caixas e o total em reais saem exatos, sem anotação manual.
#
# Por que sintético: sem moedas para fotografar, montar as fotos por programa é a forma de ter centenas de
# imagens anotadas. A variação de fundo, luz e posição existe para o modelo aprender a moeda, e não um cenário.
#
# Uso: python gerar_dataset.py   -> cria dataset/{train,valid,test}/{images,labels} e dataset/data.yaml
import glob, os, random
import cv2
import numpy as np

# Limites do enunciado: no mínimo 60 imagens (recomendado 100 ou mais), de 5 a 40 moedas por imagem,
# divididas em treino (70%), validação (20%) e teste (10%). 200 imagens compensam, em parte, a pouca variedade
# de um dataset sintético (são só 20 recortes de moedas).
IMAGENS = {"train": 140, "valid": 40, "test": 20}
MIN_MOEDAS, MAX_MOEDAS = 5, 40
LARGURA, ALTURA = 1280, 960  # proporção 4:3, a mesma das fotos de celular

# Diâmetros reais da 2a família do real. Colar cada moeda no tamanho proporcional ao real preserva a diferença
# de tamanho entre elas (ex.: 10c tem 20 mm e 25c tem 25 mm), uma pista importante para separar valores.
DIAMETRO_MM = {"5c": 22, "10c": 20, "25c": 25, "50c": 23, "1real": 27}
# Uma classe por valor e face ("5c_valor", "5c_efigie", ...): as duas faces da mesma moeda são muito diferentes,
# e o notebook compara esta definição com a de uma classe por valor.
CLASSES = [f"{v}_{f}" for v in DIAMETRO_MM for f in ["valor", "efigie"]]
# Recortes com fundo transparente (canal alfa), lidos uma vez só e reaproveitados em todas as imagens.
RECORTES = {c: [cv2.imread(p, cv2.IMREAD_UNCHANGED) for p in sorted(glob.glob(f"moedas_base/{c}_*.png"))]
            for c in CLASSES}


def fundo():
    # Sorteia um fundo de mesa de madeira, papel, tecido ou cor lisa, com ruído. Fundos variados evitam que o
    # modelo associe uma moeda a um tipo de mesa e o obrigam a olhar para a própria moeda.
    y, x = np.mgrid[0:ALTURA, 0:LARGURA].astype(np.float32)
    ruido = cv2.GaussianBlur(np.random.randn(ALTURA, LARGURA).astype(np.float32), (0, 0), 2)
    tipo = random.choice(["madeira", "papel", "tecido", "liso"])
    if tipo == "madeira":
        # cor amarronzada, veios ondulados (seno deformado) e fibras longas (ruído borrado só na horizontal)
        cor = np.array([random.uniform(40, 90), random.uniform(80, 130), random.uniform(120, 190)])
        veios = np.sin((y + 25 * np.sin(x / random.uniform(80, 300))) / random.uniform(4, 12))
        fibras = cv2.GaussianBlur(np.random.randn(ALTURA, LARGURA).astype(np.float32), (0, 0), sigmaX=40, sigmaY=1)
        textura = 1 + 0.08 * veios + 0.6 * fibras + 0.03 * ruido
    elif tipo == "papel":
        # quase branco, com leve tom de cor e textura fina, como uma folha sob luz ambiente
        cor = np.full(3, random.uniform(200, 245)) + np.random.uniform(-10, 10, 3)
        textura = 1 + 0.02 * ruido
    elif tipo == "tecido":
        # trama em xadrez fino (produto de dois senos) sobre uma cor qualquer
        cor = np.random.uniform(40, 200, 3)
        p = random.uniform(3, 6)
        textura = 1 + 0.06 * np.sin(x * 2 * np.pi / p) * np.sin(y * 2 * np.pi / p) + 0.05 * ruido
    else:
        cor = np.random.uniform(30, 220, 3)
        textura = 1 + 0.03 * ruido
    img = textura[..., None] * cor
    if random.random() < 0.5:  # metade das vezes os veios ficam na vertical, para não ter direção preferida
        img = cv2.resize(img.transpose(1, 0, 2), (LARGURA, ALTURA))
    return img


def preparar_moeda(classe, px_por_mm):
    # Prepara um recorte da moeda para colar: no tamanho certo para a distância da câmera, girado (moeda não tem
    # orientação), levemente achatado (simula a câmera um pouco inclinada) e com brilho variado (luz diferente).
    rec = random.choice(RECORTES[classe]).astype(np.float32)
    d = DIAMETRO_MM[classe.split("_")[0]] * px_por_mm * random.uniform(0.98, 1.02)
    rec = cv2.resize(rec, (int(d), int(d * random.uniform(0.93, 1.0))), interpolation=cv2.INTER_AREA)
    # O quadrado de destino é 5% maior que a moeda para que os cantos não sejam cortados na rotação.
    lado = int(d * 1.05)
    giro = cv2.getRotationMatrix2D((rec.shape[1] / 2, rec.shape[0] / 2), random.uniform(0, 360), 1)
    giro[:, 2] += [(lado - rec.shape[1]) / 2, (lado - rec.shape[0]) / 2]  # centraliza a moeda no quadrado
    rec = cv2.warpAffine(rec, giro, (lado, lado), flags=cv2.INTER_LINEAR)
    # brilho e contraste só nos canais de cor; o canal alfa (transparência) fica intacto
    rec[..., :3] = rec[..., :3] * random.uniform(0.8, 1.2) + random.uniform(-25, 25)
    return np.clip(rec, 0, 255)


def colar(img, rec, x, y):
    # Cola a moeda com x, y no canto superior esquerdo. Antes, escurece uma sombra (o alfa borrado e deslocado),
    # porque nas fotos reais toda moeda projeta sombra, e sem ela a moeda pareceria "flutuar" sobre a mesa.
    h, w = rec.shape[:2]
    alfa = rec[..., 3:] / 255
    sombra = cv2.GaussianBlur(alfa, (0, 0), w * 0.04)[..., None]
    dx, dy = int(w * 0.05), int(w * 0.05)
    img[y + dy:y + dy + h, x + dx:x + dx + w] *= 1 - 0.5 * sombra
    # mistura pelo alfa: dentro do círculo fica a moeda, fora dele continua o fundo
    img[y:y + h, x:x + w] = img[y:y + h, x:x + w] * (1 - alfa) + rec[..., :3] * alfa


def gerar_imagem():
    img = fundo()
    # Escala sorteada por imagem (pixels por milímetro): simula a câmera mais perto ou mais longe da mesa. É a
    # mesma para todas as moedas da imagem, como numa foto de verdade, para manter os tamanhos relativos.
    px_por_mm = random.uniform(3.0, 4.5)
    colocadas = []  # (classe, cx, cy, raio, caixa)
    for _ in range(random.randint(MIN_MOEDAS, MAX_MOEDAS)):
        classe = random.choice(CLASSES)
        rec = preparar_moeda(classe, px_por_mm)
        h, w = rec.shape[:2]
        r = w / 2
        # Procura um lugar livre em até 200 tentativas. Moedas podem encostar (a distância mínima é 97% da soma
        # dos raios), mas não se cobrem, porque uma moeda escondida teria rótulo sem estar visível.
        for _ in range(200):
            x, y = random.randint(10, LARGURA - w - 20), random.randint(10, ALTURA - h - 20)
            cx, cy = x + w / 2, y + h / 2
            if all(np.hypot(cx - c[1], cy - c[2]) >= 0.97 * (r + c[3]) for c in colocadas):
                break
        else:
            continue  # não coube: a imagem fica com uma moeda a menos, o que só muda o total sorteado
        colar(img, rec, x, y)
        # Caixa justa calculada a partir da parte visível da moeda (alfa acima da metade), e não do quadrado do
        # recorte, para a caixa anotada coincidir com a borda da moeda como numa anotação feita à mão.
        ys, xs = np.nonzero(rec[..., 3] > 127)
        colocadas.append((classe, cx, cy, r, (x + xs.min(), y + ys.min(), x + xs.max(), y + ys.max())))

    # Defeitos de uma foto de verdade, aplicados na imagem inteira: luz desigual (um lado mais claro, como luz de
    # janela), ruído do sensor e, em metade das imagens, um leve desfoque (foco imperfeito ou mão tremida).
    y, x = np.mgrid[0:ALTURA, 0:LARGURA].astype(np.float32)
    ang = random.uniform(0, 2 * np.pi)
    grad = (x * np.cos(ang) + y * np.sin(ang)) / np.hypot(LARGURA, ALTURA)
    img *= (random.uniform(0.75, 1.1) + random.uniform(0, 0.4) * grad)[..., None]
    img += np.random.randn(*img.shape) * random.uniform(1, 5)
    img = np.clip(img, 0, 255).astype(np.uint8)
    if random.random() < 0.5:
        img = cv2.GaussianBlur(img, (0, 0), random.uniform(0.5, 1.2))
    return img, colocadas


# Sementes fixas: quem rodar o script (inclusive o notebook no Colab) obtém exatamente as mesmas imagens, o que
# torna os resultados reproduzíveis.
random.seed(42)
np.random.seed(42)
for split, n in IMAGENS.items():
    os.makedirs(f"dataset/{split}/images", exist_ok=True)
    os.makedirs(f"dataset/{split}/labels", exist_ok=True)
    for i in range(n):
        img, colocadas = gerar_imagem()
        nome = f"dataset/{split}/%s/{split}_{i:03d}"
        # qualidade JPEG sorteada, porque cada celular comprime as fotos de um jeito
        cv2.imwrite(nome % "images" + ".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, random.randint(75, 95)])
        # Rótulo YOLO: uma linha por moeda com classe, centro, largura e altura relativos ao tamanho da imagem
        # (0 a 1), para valer em qualquer resolução que o treino use.
        with open(nome % "labels" + ".txt", "w") as f:
            for classe, _, _, _, (x1, y1, x2, y2) in colocadas:
                f.write(f"{CLASSES.index(classe)} {(x1 + x2) / 2 / LARGURA:.6f} {(y1 + y2) / 2 / ALTURA:.6f} "
                        f"{(x2 - x1) / LARGURA:.6f} {(y2 - y1) / ALTURA:.6f}\n")
    print(split, n, "imagens")

with open("dataset/data.yaml", "w") as f:
    f.write(f"train: train/images\nval: valid/images\ntest: test/images\nnc: {len(CLASSES)}\nnames: {CLASSES}\n")
