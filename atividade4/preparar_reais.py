# Separa as fotos reais do Brazilian Coin Detection Dataset (IEEE DataPort, CC BY 4.0) em teste, demonstração,
# treino e validação, e converte os círculos anotados (formato labelme) em caixas no formato YOLO, com as classes
# por valor do notebook.
#
# Por que fotos reais: o modelo treinado só no dataset sintético erra muito em fotos de celular. As fotos de teste
# medem esse erro, e as de treino e validação entram numa segunda etapa de transfer learning.
#
# Uso: python preparar_reais.py <pasta dataset/ do download> reais
import json, glob, os, sys, shutil

ORIG, DEST = sys.argv[1], sys.argv[2]
# Rótulos do dataset original (valor em centavos), na mesma ordem de CLASSES no notebook (5c, 10c, 25c, 50c,
# 1real). O índice de cada rótulo nesta lista vira o número da classe no arquivo YOLO, então a ordem precisa bater.
CLASSES = ["5", "10", "25", "50", "100"]
MIN_MOEDAS = 5        # mínimo de moedas por foto no treino e na validação, o mesmo mínimo do enunciado (5 a 40)
FOTOS_POR_SESSAO = 6  # fotos de cada sessão no treino e na validação
A_CADA_VALID = 5      # 1 sessão de cada 5 vai para a validação, as outras para o treino

# Lê cada anotação: (tempo, total em centavos, nº de moedas, tem rótulo fora das classes, arquivo).
# O nome do arquivo é "<total>_<tempo>.json", e o tempo (segundos) permite reconstruir a ordem das fotos.
r = []
for f in glob.glob(os.path.join(ORIG, "*.json")):
    v, t = os.path.basename(f)[:-5].split("_")
    s = json.load(open(f))["shapes"]
    r.append((int(t), int(v), len(s), any(x["label"] not in CLASSES for x in s), f))
r.sort()

# Agrupa as fotos em sessões. O autor fotografou o mesmo conjunto de moedas várias vezes seguidas (a cada ~6 s),
# mudando as moedas de lugar entre uma foto e outra. Fotos seguidas com o mesmo total são, portanto, as mesmas
# moedas: se uma sessão aparecesse no treino e no teste ao mesmo tempo, o teste ficaria fácil demais (vazamento).
# Por isso a divisão entre teste, treino e validação é feita por sessão, nunca por foto.
ses, cur = [], [r[0]]
for a in r[1:]:
    if a[0] - cur[-1][0] > 60 or a[1] != cur[-1][1]:  # mais de 1 minuto de intervalo ou total diferente
        ses.append(cur); cur = [a]
    else:
        cur.append(a)
ses.append(cur)

# Em cada sessão, só fotos sem rótulo fora das classes (algumas têm um "finger", o dedo de quem fotografou),
# ordenadas da que tem mais moedas para a que tem menos. Mais moedas por foto deixa a foto mais parecida com o
# uso pretendido (uma mesa com várias moedas) e dá mais exemplos de treino por imagem. As sessões são ordenadas
# do mesmo jeito, pelo nº de moedas da melhor foto.
sessoes = []
for s in ses:
    ok = sorted((x for x in s if not x[3]), key=lambda x: (-x[2], x[0]))
    if ok:
        sessoes.append(ok)
sessoes.sort(key=lambda s: (-s[0][2], s[0][0]))

# Teste: a melhor foto de cada uma das 10 sessões com mais moedas. Uma foto por sessão, para que o teste cubra
# 10 conjuntos de moedas diferentes em vez de 10 arranjos do mesmo conjunto.
teste = [s[0] for s in sessoes[:10]]
# Demonstração: uma foto com 11 moedas e duas das poucas com moeda de 1 real, de sessões fora do teste.
nomes_demo = ("80_1477850610", "150_1477864224", "130_1477863000")
demo = [x for x in r if os.path.basename(x[4])[:-5] in nomes_demo]

# Treino e validação da 2a etapa: as sessões restantes com pelo menos MIN_MOEDAS moedas, já ordenadas da que tem
# mais moedas para a que tem menos, sem as sessões da demonstração (para a demonstração continuar inédita).
# De cada sessão entram as FOTOS_POR_SESSAO fotos com mais moedas: como as moedas mudam de lugar a cada foto,
# várias fotos da mesma sessão mostram arranjos, sombras e reflexos diferentes, o que ajuda o modelo a generalizar.
# A validação fica com sessões inteiras (1 de cada A_CADA_VALID), separadas do treino pelo mesmo motivo do teste.
# Às vezes o autor fez uma pausa de alguns minutos e voltou a fotografar as mesmas moedas, o que cria uma
# "sessão" nova com o mesmo total. Para não haver vazamento, fica de fora qualquer sessão com o mesmo total de
# uma foto de teste ou de demonstração tirada até 1 hora antes ou depois dela.
protegidas = teste + demo
def perto_de_protegida(s):
    return any(x[1] == p[1] and abs(x[0] - p[0]) < 3600 for x in s for p in protegidas)

treino, valid = [], []
restantes = [s for s in sessoes[10:] if s[0][2] >= MIN_MOEDAS and not perto_de_protegida(s)]
for i, s in enumerate(restantes):
    fotos = [x for x in s if x[2] >= MIN_MOEDAS][:FOTOS_POR_SESSAO]
    (valid if i % A_CADA_VALID == A_CADA_VALID - 1 else treino).extend(fotos)

escolha = {"teste": teste, "demo": demo, "treino": treino, "valid": valid}
for conj, fotos in escolha.items():
    os.makedirs(f"{DEST}/{conj}/images", exist_ok=True); os.makedirs(f"{DEST}/{conj}/labels", exist_ok=True)
    for t, v, n, _, f in fotos:
        d = json.load(open(f)); W, H = d["imageWidth"], d["imageHeight"]
        nome = os.path.basename(f)[:-5]
        shutil.copy(f[:-5] + ".jpg", f"{DEST}/{conj}/images/{nome}.jpg")
        linhas = []
        for x in d["shapes"]:
            # Cada moeda está anotada como um círculo: o 1o ponto é o centro e o 2o um ponto da borda. A caixa
            # YOLO é o quadrado que contém o círculo (centro ± raio), cortado nas bordas da imagem para não sair
            # dela, e depois escrita relativa à largura e à altura, como o formato YOLO exige.
            (cx, cy), (px, py) = x["points"][:2]
            rr = ((cx - px) ** 2 + (cy - py) ** 2) ** 0.5
            x1, y1, x2, y2 = max(0, cx - rr), max(0, cy - rr), min(W, cx + rr), min(H, cy + rr)
            linhas.append(f"{CLASSES.index(x['label'])} {(x1+x2)/2/W:.6f} {(y1+y2)/2/H:.6f} {(x2-x1)/W:.6f} {(y2-y1)/H:.6f}")
        # newline="\n" para o arquivo sair igual no Windows e no Linux (Colab)
        open(f"{DEST}/{conj}/labels/{nome}.txt", "w", newline="\n").write("\n".join(linhas) + "\n")
    print(conj, len(fotos), "fotos,", sum(x[2] for x in fotos), "moedas")
