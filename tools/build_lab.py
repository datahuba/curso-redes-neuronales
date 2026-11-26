"""Genera el laboratorio interactivo (HTML autocontenido) a partir de la plantilla.

Uso (desde la raiz del repo):
    python tools/build_lab.py

Salida:
    docs/lab/LABORATORIO_TEMA3.html   (una sola pagina, sin internet, con los datos dentro)

Que hace:
1. Lee proyecto/datos/mnist.npz (MNIST local) y toma 4 clases x 300 imagenes.
2. Reduce cada imagen de 28x28 a 14x14 y la cuantiza a 0..15 (1 caracter hex por pixel).
3. Baraja con semilla fija y separa 900 para entrenar / 300 de examen.
4. Calcula las cifras de referencia (perceptron, sigmoide, softmax, XOR) con NumPy,
   usando EXACTAMENTE los mismos algoritmos que ejecuta el JavaScript de la pagina.
5. Sustituye en la plantilla los datos y los marcadores {{P01_ACC}}, {{SG_ACC}}, ...
"""
import os
import sys

import numpy as np

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLANTILLA = os.path.join(RAIZ, "docs", "lab", "LABORATORIO_TEMA3.template.html")
SALIDA = os.path.join(RAIZ, "docs", "lab", "LABORATORIO_TEMA3.html")
MNIST = os.path.join(RAIZ, "proyecto", "datos", "mnist.npz")

CLASES = [0, 1, 3, 5]
POR_CLASE = 300
DIM = 14
D = DIM * DIM
ENTRENAR = 900
SEMILLA = 7


# ---------------------------------------------------------------- datos
def cargar_datos():
    if not os.path.exists(MNIST):
        sys.exit(
            "Falta " + MNIST + "\n"
            "El laboratorio lleva dentro los datos de MNIST. Descarga el .npz del curso\n"
            "(carpeta proyecto/datos/) y vuelve a ejecutar este script."
        )
    d = np.load(MNIST)
    xt, yt = d["x_train"], d["y_train"]

    def reducir(xs):
        b = xs.reshape(xs.shape[0], DIM, 2, DIM, 2).mean(axis=(2, 4))
        return np.round(b / 255.0 * 15.0).astype(np.int64)

    X = np.concatenate([reducir(xt[np.where(yt == c)[0][:POR_CLASE]]) for c in CLASES])
    Y = np.concatenate([np.full(POR_CLASE, c) for c in CLASES])
    X = X.reshape(len(X), D).astype(np.float64) / 15.0
    perm = np.random.default_rng(SEMILLA).permutation(len(X))
    return X[perm], Y[perm]


# ---------------------------------------------------------------- algoritmos (mismos que el JS)
def perceptron(X, y, eta=0.1, ep=15):
    """Mismo acumulador que el JavaScript de la pagina (suma secuencial, no BLAS),
    para que los numeros por epoca coincidan bit a bit."""
    w = np.zeros(D); b = 0.0; errs = []
    for _ in range(ep):
        err = 0
        for x, t in zip(X, y):
            z = b
            for k in range(D):
                z += x[k] * w[k]
            er = t - (1 if z > 0 else 0)
            if er != 0:
                err += 1
                s = eta * er
                for k in range(D):
                    w[k] += s * x[k]
                b += s
        errs.append(err)
    return w, b, errs


def predecir_perceptron(w, b, x):
    z = b
    for k in range(D):
        z += w[k] * x[k]
    return 1 if z > 0 else 0


def sigmoide(z):
    return 1 / (1 + np.exp(-np.clip(z, -500, 500)))


def sigmGD(X, y, eta=1.0, ep=120):
    w = np.zeros(D); b = 0.0; loss = []
    for _ in range(ep):
        p = sigmoide(X @ w + b)
        loss.append(-np.mean(y * np.log(p + 1e-12) + (1 - y) * np.log(1 - p + 1e-12)))
        w = w - eta * (X.T @ (p - y) / len(X))
        b = b - eta * (p - y).mean()
    return w, b, loss


def softmax_z(z):
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def softmax_red(X, Yi, K, eta=1.0, ep=200):
    W = np.zeros((D, K)); B = np.zeros(K); loss = []
    Yh = np.eye(K)[Yi]
    for _ in range(ep):
        P = softmax_z(X @ W + B)
        loss.append(-np.mean(np.log(P[np.arange(len(X)), Yi] + 1e-12)))
        G = (P - Yh) / len(X)
        W = W - eta * (X.T @ G)
        B = B - eta * G.sum(axis=0)
    return W, B, loss


class LCG:
    """Mismo LCG que el JavaScript de la pagina (Math.imul)."""

    def __init__(self, seed=20261125):
        self.s = seed & 0xFFFFFFFF

    def next_u(self):
        self.s = (self.s * 1664525 + 1013904223) % (2 ** 32)
        return self.s / 2 ** 32

    def mat(self, r, c, a):
        return np.array([[(self.next_u() * 2 - 1) * a for _ in range(c)] for _ in range(r)])


def xor_red(H=3, eta=1.0, ep=1000):
    X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], float)
    Y = np.array([[0], [1], [1], [0]], float)
    g = LCG()
    W1 = g.mat(2, H, np.sqrt(1 / 2)); b1 = np.zeros(H)
    W2 = g.mat(H, 1, np.sqrt(1 / H)); b2 = np.zeros(1)
    loss = []
    for _ in range(ep):
        Z1 = X @ W1 + b1
        A1 = np.tanh(Z1)
        P = sigmoide(A1 @ W2 + b2)                      # (4,1)
        loss.append(-np.mean(Y * np.log(P + 1e-12) + (1 - Y) * np.log(1 - P + 1e-12)))
        dA1 = ((P - Y) @ W2.T) / 4                       # (4,H)
        dZ1 = dA1 * (1 - A1 ** 2)
        W1 = W1 - eta * (X.T @ dZ1)
        b1 = b1 - eta * dZ1.mean(axis=0)
        W2 = W2 - eta * (A1.T @ ((P - Y) / 4))
        b2 = b2 - eta * ((P - Y) / 4).sum(axis=0)
    P = sigmoide(np.tanh(X @ W1 + b1) @ W2 + b2)
    acc = ((P > 0.5).astype(float) == Y).mean()
    return loss, acc


# ---------------------------------------------------------------- referencias
def referencias(X, Y):
    Xtr, Ytr = X[:ENTRENAR], Y[:ENTRENAR]
    Xte, Yte = X[ENTRENAR:], Y[ENTRENAR:]
    mapa = {c: i for i, c in enumerate(CLASES)}
    ref = {}

    # 3.1 perceptron 0 vs 1   (convencion del curso: y = 1 si es B)
    m = np.isin(Ytr, [0, 1])
    w, b, errs = perceptron(Xtr[m], (Ytr[m] == 1).astype(float))
    ex01 = np.isin(Yte, [0, 1])
    pred = np.array([predecir_perceptron(w, b, x) for x in Xte[ex01]])
    real = (Yte[ex01] == 1).astype(float)
    ref["P01_EPOCA"] = str(errs.index(0) + 1)
    ref["P01_ACC"] = "%.1f %%" % (100 * (pred == real).mean())
    ref["P01_ERRS"] = ", ".join(str(e) for e in errs[:8])

    # 3.2 perceptron 3 vs 5   (y = 1 si es 5)
    m = np.isin(Ytr, [3, 5])
    _, _, errs35 = perceptron(Xtr[m], (Ytr[m] == 5).astype(float))
    ref["P35_ERRS"] = ", ".join(str(e) for e in errs35[:8])

    # 3.3 sigmoide 3 vs 5
    ws, bs, loss = sigmGD(Xtr[m], (Ytr[m] == 5).astype(float))
    p = sigmoide(Xte[np.isin(Yte, [3, 5])] @ ws + bs)
    ref["SG_ACC"] = "%.0f" % (100 * ((p > 0.5) == (Yte[np.isin(Yte, [3, 5])] == 5)).mean())
    ref["SG_LOSS"] = "%.4f" % loss[-1]

    # 3.4 softmax 4 clases
    Yi = np.array([mapa[c] for c in Ytr])
    W, B, loss = softmax_red(Xtr, Yi, 4)
    P = softmax_z(Xte @ W + B)
    ref["SM_ACC"] = "%.0f" % (100 * (P.argmax(axis=1) == np.array([mapa[c] for c in Yte])).mean())
    ref["SM_LOSS"] = "%.4f" % loss[-1]

    # 4.1 XOR con capa oculta
    xloss, xacc = xor_red()
    ref["XO_LOSS0"] = "%.4f" % xloss[0]
    ref["XO_LOSS1"] = "%.4f" % xloss[-1]
    ref["XO_ACC"] = str(int(round(xacc * 4)))
    return ref


# ---------------------------------------------------------------- main
def main():
    X, Y = cargar_datos()
    ref = referencias(X, Y)

    hex_datos = "".join("%x" % int(round(v * 15)) for v in X.ravel())
    etiquetas = "".join(str(int(v)) for v in Y)

    datos_js = (
        "const LAB_DATA = {\n"
        "  clases: [" + ", ".join(str(c) for c in CLASES) + "],\n"
        "  n: %d,\n  d: %d,\n  train: %d,\n"
        '  hex: "%s",\n  y: "%s"\n};\n' % (len(X), D, ENTRENAR, hex_datos, etiquetas)
    )
    # versión de esta compilación: el panel docente marca a quien sigue con una página vieja
    import time
    datos_js += 'const LAB_VERSION = "%s";\n' % time.strftime("%Y%m%d%H%M%S")

    with open(PLANTILLA, encoding="utf-8") as f:
        html = f.read()
    if "/*__DATOS__*/" not in html:
        sys.exit("Falta el marcador /*__DATOS__*/ en la plantilla.")
    html = html.replace("/*__DATOS__*/", datos_js)
    for k, v in ref.items():
        html = html.replace("{{%s}}" % k, v)
    if "{{" in html:
        import re
        pendientes = sorted(set(re.findall(r"\{\{(\w+)\}\}", html)))
        sys.exit("Marcadores sin reemplazar: " + ", ".join(pendientes))

    with open(SALIDA, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)

    print("Escrito: %s (%.0f KB)" % (os.path.relpath(SALIDA, RAIZ), os.path.getsize(SALIDA) / 1024))
    print("Datos: %d imagenes de %dx%d, %d para entrenar y %d de examen" % (len(X), DIM, DIM, ENTRENAR, len(X) - ENTRENAR))
    for k in sorted(ref):
        print("  %-10s %s" % (k, ref[k]))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
