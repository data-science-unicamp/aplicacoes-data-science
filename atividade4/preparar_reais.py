# Separa as fotos reais de teste e de demonstração do Brazilian Coin Detection Dataset (IEEE DataPort, CC BY 4.0)
# e converte os círculos anotados (labelme) em caixas no formato YOLO, com as classes por valor do notebook.
# Uso: python preparar_reais.py <pasta dataset/ do download> reais
import json, glob, os, sys, shutil

ORIG, DEST = sys.argv[1], sys.argv[2]
CLASSES = ["5", "10", "25", "50", "100"]  # ordem de CLASSES no notebook: 5c, 10c, 25c, 50c, 1real

# fotos (tempo, total em centavos, nº de moedas, tem rótulo fora das classes, arquivo)
r = []
for f in glob.glob(os.path.join(ORIG, "*.json")):
    v, t = os.path.basename(f)[:-5].split("_")
    s = json.load(open(f))["shapes"]
    r.append((int(t), int(v), len(s), any(x["label"] not in CLASSES for x in s), f))
r.sort()
# o autor fotografou a mesma mesa a cada 6 s: fotos seguidas com o mesmo total formam uma sessão quase idêntica,
# então cada foto escolhida vem de uma sessão diferente
ses, cur = [], [r[0]]
for a in r[1:]:
    if a[0] - cur[-1][0] > 60 or a[1] != cur[-1][1]:
        ses.append(cur); cur = [a]
    else:
        cur.append(a)
ses.append(cur)
# de cada sessão, a foto com mais moedas e sem rótulo estranho (dedo); sessões ordenadas pelo nº de moedas
melhores = []
for s in ses:
    ok = [x for x in s if not x[3]]
    if ok:
        melhores.append(max(ok, key=lambda x: (x[2], -x[0])))
melhores.sort(key=lambda x: (-x[2], x[0]))
# demonstração: uma foto com 11 moedas e duas das poucas com moeda de 1 real, de sessões fora do teste
demo = [x for x in r if os.path.basename(x[4])[:-5] in ("80_1477850610", "150_1477864224", "130_1477863000")]
escolha = {"teste": melhores[:10], "demo": demo}
for conj, fotos in escolha.items():
    os.makedirs(f"{DEST}/{conj}/images", exist_ok=True); os.makedirs(f"{DEST}/{conj}/labels", exist_ok=True)
    for t, v, n, _, f in fotos:
        d = json.load(open(f)); W, H = d["imageWidth"], d["imageHeight"]
        nome = os.path.basename(f)[:-5]
        shutil.copy(f[:-5] + ".jpg", f"{DEST}/{conj}/images/{nome}.jpg")
        linhas = []
        for x in d["shapes"]:
            (cx, cy), (px, py) = x["points"][:2]
            rr = ((cx - px) ** 2 + (cy - py) ** 2) ** 0.5
            x1, y1, x2, y2 = max(0, cx - rr), max(0, cy - rr), min(W, cx + rr), min(H, cy + rr)
            linhas.append(f"{CLASSES.index(x['label'])} {(x1+x2)/2/W:.6f} {(y1+y2)/2/H:.6f} {(x2-x1)/W:.6f} {(y2-y1)/H:.6f}")
        open(f"{DEST}/{conj}/labels/{nome}.txt", "w", newline="\n").write("\n".join(linhas) + "\n")
        print(conj, nome, n, "moedas", "R$", v / 100, {x["shape_type"] for x in d["shapes"]})
