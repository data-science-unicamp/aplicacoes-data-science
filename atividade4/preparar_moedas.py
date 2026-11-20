# Recorta cada moeda das fotos em originais/ (Wikimedia Commons, domínio público ou CC0, baixadas à mão
# pelos links de moedas_base/FONTES.md) e salva em moedas_base/<classe>_<n>.png com fundo transparente.
# Roda uma vez só; o gerador usa os recortes.
import os, urllib.parse
import cv2
import numpy as np

# foto -> classes das moedas da esquerda para a direita
FOTOS = {
    "Brazil R$0.05 2010.jpg": ["5c_valor", "5c_efigie"],
    "5 Centavos (2022) - Vorderseite.jpg": ["5c_valor"],
    "5 Centavos (2022) - Rückseite.jpg": ["5c_efigie"],
    "Brazil R$0.10 1998.jpg": ["10c_valor", "10c_efigie"],
    "10 Centavos (2018) - Vorderseite.jpg": ["10c_valor"],
    "10 Centavos (2018) - Rückseite.jpg": ["10c_efigie"],
    "Brazil R$0.25 2013.jpg": ["25c_valor", "25c_efigie"],
    "25 Centavos (2021) - Vorderseite.jpg": ["25c_valor"],
    "25 Centavos (2021) - Rückseite.jpg": ["25c_efigie"],
    "Brazil R$0.50 2013.jpg": ["50c_valor", "50c_efigie"],
    "50 Centavos (2018) - Vorderseite.jpg": ["50c_valor"],
    "50 Centavos (2018) - Rückseite.jpg": ["50c_efigie"],
    "Brazil R$01 2013.jpg": ["1real_valor", "1real_efigie"],
    "Brasil coin 1 real.jpg": ["1real_valor"],
    "Brasil coin 1 real-2.jpg": ["1real_efigie"],
}
LADO = 300  # tamanho do recorte salvo, em pixels

os.makedirs("moedas_base", exist_ok=True)
fontes = ["# Fontes das moedas\n", "Fotos do Wikimedia Commons (domínio público ou CC0), recortadas por `preparar_moedas.py`.\n"]

for foto, classes in FOTOS.items():
    foto_inteira = cv2.imdecode(np.fromfile(os.path.join("originais", foto), np.uint8), cv2.IMREAD_COLOR)
    largura = foto_inteira.shape[1] // len(classes)  # foto com 2 moedas: uma em cada metade

    for k, classe in enumerate(classes):
        img = foto_inteira[:, k * largura:(k + 1) * largura]
        # moeda = maior região que difere da cor do fundo (mediana da borda)
        borda = np.concatenate([img[0], img[-1], img[:, 0], img[:, -1]])
        dist = np.linalg.norm(img.astype(float) - np.median(borda, axis=0), axis=2).astype(np.uint8)
        _, mascara = cv2.threshold(cv2.GaussianBlur(dist, (9, 9), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
        contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        (cx, cy), r = cv2.minEnclosingCircle(max(contornos, key=cv2.contourArea))
        r *= 0.98  # tira a borda do fundo que sobra em volta da moeda
        m = int(r) + 1  # margem para o recorte não sair da foto
        ampla = cv2.copyMakeBorder(img, m, m, m, m, cv2.BORDER_REPLICATE)
        quadrado = ampla[int(cy - r) + m:int(cy + r) + m, int(cx - r) + m:int(cx + r) + m]
        quadrado = cv2.resize(quadrado, (LADO, LADO), interpolation=cv2.INTER_AREA)
        alfa = np.zeros((LADO, LADO), np.uint8)
        cv2.circle(alfa, (LADO // 2, LADO // 2), LADO // 2 - 1, 255, -1, cv2.LINE_AA)
        n = len([f for f in os.listdir("moedas_base") if f.startswith(classe + "_")]) + 1
        nome = f"{classe}_{n}.png"
        cv2.imwrite(os.path.join("moedas_base", nome), np.dstack([quadrado, alfa]))
        fontes.append(f"- `{nome}`: [{foto}](https://commons.wikimedia.org/wiki/File:{urllib.parse.quote(foto.replace(' ', '_'))})")
        print(nome, "<-", foto)

open(os.path.join("moedas_base", "FONTES.md"), "w", encoding="utf-8").write("\n".join(fontes) + "\n")
