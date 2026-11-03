"""Clase 4: entrenar una neurona con descenso por gradiente (regla delta), ADALINE y red de varias salidas.

Ejecutar desde la carpeta del repo, con el ambiente nni activo:
    python docs/practica_04.py              -> resultados en la terminal
    python docs/practica_04.py --graficar   -> además muestra las gráficas
"""
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))


def sigmoide(h):
    return 1 / (1 + np.exp(-h))


def mse(y, y_hat):
    return np.mean((np.asarray(y) - np.asarray(y_hat)) ** 2)


# --- 1. Un paso de la regla delta: delta = (y - y_hat) * f'(h);  w <- w + eta * delta * x ---
def paso_delta(w, b, x, y, eta):
    h = np.dot(w, x) + b
    y_hat = sigmoide(h)
    delta = (y - y_hat) * y_hat * (1 - y_hat)       # f'(h) de la sigmoide = y_hat (1 - y_hat)
    return w + eta * delta * x, b + eta * delta, y_hat, delta


# --- 2. Entrenamiento completo por lotes: OR con una neurona sigmoide ---
def entrenar(X, y, eta=1.0, epocas=2000, semilla=0):
    rng = np.random.default_rng(semilla)
    n = X.shape[1]
    w = rng.uniform(-1 / np.sqrt(n), 1 / np.sqrt(n), size=n)     # inicialización de Xavier
    b = 0.0
    perdidas = []
    for _ in range(epocas):
        y_hat = sigmoide(X @ w + b)
        delta = (y - y_hat) * y_hat * (1 - y_hat)
        w = w + eta * (delta @ X) / len(X)                       # promedio de los incrementos
        b = b + eta * delta.mean()
        perdidas.append(mse(y, sigmoide(X @ w + b)))
    return w, b, perdidas


# --- 3. ADALINE: activación lineal, regresión de salario vs. años de experiencia ---
def adaline(x, y, eta=0.01, epocas=5000):
    xm, xs, ym, ys = x.mean(), x.std(), y.mean(), y.std()      # estandarizar acelera mucho
    xn, yn = (x - xm) / xs, (y - ym) / ys
    w = b = 0.0
    for _ in range(epocas):
        e = yn - (w * xn + b)
        w += eta * np.mean(e * xn)
        b += eta * np.mean(e)
    pendiente = w * ys / xs                                       # volver a unidades originales
    return pendiente, ym + b * ys - pendiente * xm


# --- 4. Red de una capa con varias salidas: H = X W + B ---
def red_varias_salidas(X, W, B):
    H = X @ W + B
    return H, sigmoide(H)


if __name__ == "__main__":
    print("1) Un paso de la regla delta (valores del notebook 1_06)")
    w, b, x, y = np.array([0.1, 0.2]), 0.0, np.array([1.0, 1.0]), 1.0
    w2, b2, y_hat, delta = paso_delta(w, b, x, y, eta=2.0)
    y_hat2 = sigmoide(np.dot(w2, x) + b2)
    print(f"   y_hat = {y_hat:.4f}  delta = {delta:.4f}  nuevos w = {np.round(w2, 4)}  b = {b2:.4f}")
    print(f"   pérdida ½(y - y_hat)²: {0.5 * (y - y_hat) ** 2:.4f} -> {0.5 * (y - y_hat2) ** 2:.4f}")

    print("\n2) Entrenamiento completo: OR con una neurona sigmoide")
    X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
    y_or = np.array([0, 1, 1, 1], dtype=float)
    w, b, perdidas = entrenar(X, y_or)
    pred = (sigmoide(X @ w + b) > 0.5).astype(int)
    print(f"   pérdida (MSE): {perdidas[0]:.4f} -> {perdidas[-1]:.4f}   predicciones = {pred.tolist()}")
    y_xor = np.array([0, 1, 1, 0], dtype=float)
    _, _, p_xor = entrenar(X, y_xor)
    print(f"   XOR: la pérdida se queda en {p_xor[-1]:.3f} -> una sola neurona no puede (hace falta otra capa)")

    print("\n3) ADALINE: salario vs. años de experiencia")
    datos = np.genfromtxt(os.path.join(AQUI, "..", "notebooks", "files", "Salary_dataset.csv"),
                          delimiter=",", skip_header=1)
    anios, salario = datos[:, 1], datos[:, 2]
    m, c = adaline(anios, salario)
    print(f"   salario ≈ {m:,.0f} · años + {c:,.0f}    (5 años -> {m * 5 + c:,.0f})")

    print("\n4) Red de una capa con 2 entradas y 2 salidas (ejemplo del libro, corregido)")
    H, Y = red_varias_salidas(np.array([8, 4]), np.array([[-0.1, 0.6], [-0.8, 0.3]]), np.array([-0.7, 0.3]))
    print(f"   H = {H}   y_hat = {np.round(Y, 4)}   parámetros = (2 + 1) · 2 = 6")

    # comprobaciones
    assert abs(delta - 0.10403) < 1e-4 and 0.5 * (y - y_hat2) ** 2 < 0.5 * (y - y_hat) ** 2
    assert pred.tolist() == [0, 1, 1, 1] and perdidas[-1] < perdidas[0]
    assert p_xor[-1] > 0.2
    mx, cx = np.polyfit(anios, salario, 1)
    assert abs(m - mx) < 1 and abs(c - cx) < 10
    assert np.allclose(H, [-4.7, 6.3])
    print("\nTodas las comprobaciones pasaron.")

    if "--graficar" in sys.argv:
        import matplotlib.pyplot as plt
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4))
        a1.plot(perdidas, label="OR")
        a1.plot(p_xor, label="XOR")
        a1.set_title("Pérdida durante el entrenamiento")
        a1.set_xlabel("época")
        a1.legend()
        a2.scatter(anios, salario, label="datos")
        a2.plot(anios, m * anios + c, color="tab:orange", label="ADALINE")
        a2.set_title("ADALINE: salario vs. experiencia")
        a2.legend()
        plt.tight_layout()
        plt.show()
