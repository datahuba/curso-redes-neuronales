"""Clase 5: red multicapa y retropropagación. ¡Por fin XOR!

Ejecutar desde la carpeta del repo, con el ambiente nni activo:
    python docs/practica_05.py              -> resultados en la terminal
    python docs/practica_05.py --graficar   -> además muestra la curva de aprendizaje y la frontera
"""
import sys

import numpy as np


def sigmoide(h):
    return 1 / (1 + np.exp(-h))


def adelante(X, W1, b1, W2, b2):
    """Pase hacia adelante: entrada -> oculta -> salida."""
    A1 = sigmoide(X @ W1 + b1)
    Y = sigmoide(A1 @ W2 + b2)
    return A1, Y


def entrenar_xor(n_ocultas=3, eta=2.0, epocas=5000, semilla=1):
    X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
    y = np.array([[0], [1], [1], [0]], dtype=float)
    rng = np.random.default_rng(semilla)
    W1 = rng.normal(0, 1, size=(2, n_ocultas))
    b1 = np.zeros(n_ocultas)
    W2 = rng.normal(0, 1, size=(n_ocultas, 1))
    b2 = np.zeros(1)
    perdidas = []
    for _ in range(epocas):
        A1, Y = adelante(X, W1, b1, W2, b2)
        # retropropagación
        d_salida = (y - Y) * Y * (1 - Y)                  # término de error de la salida
        d_oculta = (d_salida @ W2.T) * A1 * (1 - A1)      # se reparte hacia la capa oculta
        # incrementos (promedio de los 4 ejemplos) y actualización
        W2 += eta * A1.T @ d_salida / len(X)
        b2 += eta * d_salida.mean(axis=0)
        W1 += eta * X.T @ d_oculta / len(X)
        b1 += eta * d_oculta.mean(axis=0)
        perdidas.append(float(np.mean((y - Y) ** 2)))
    return X, y, (W1, b1, W2, b2), perdidas


def ejemplo_1_10():
    """El ejemplo del notebook 1_10: red 3-2-1, un paso de retropropagación."""
    x = np.array([0.5, 0.1, -0.2])
    objetivo, eta = 0.6, 0.5
    W_ih = np.array([[0.5, -0.6], [0.1, -0.2], [0.1, 0.7]])
    W_ho = np.array([0.1, -0.3])
    a_h = sigmoide(x @ W_ih)
    salida = sigmoide(a_h @ W_ho)
    d_o = (objetivo - salida) * salida * (1 - salida)
    d_h = d_o * W_ho * a_h * (1 - a_h)
    return a_h, salida, d_o, d_h, eta * d_o * a_h, eta * d_h * x[:, None]


if __name__ == "__main__":
    a_h, salida, d_o, d_h, dw_ho, dw_ih = ejemplo_1_10()
    print("1) Ejemplo del notebook 1_10 (red 3-2-1)")
    print(f"   salida oculta = {np.round(a_h, 4)}   salida = {salida:.4f}")
    print(f"   delta salida = {d_o:.5f}   delta oculta = {np.round(d_h, 6)}")
    print(f"   incremento oculta->salida = {np.round(dw_ho, 5)}")

    print("\n2) XOR con una red 2-3-1 entrenada con retropropagación")
    X, y, params, perdidas = entrenar_xor()
    _, Y = adelante(X, *params)
    pred = (Y.ravel() > 0.5).astype(int)
    for x, p, s in zip(X, pred, Y.ravel()):
        print(f"   {x.astype(int)} -> {s:.3f} -> {p}")
    print(f"   pérdida (MSE): {perdidas[0]:.4f} -> {perdidas[-1]:.4f}")

    # comprobaciones
    assert abs(salida - 0.4850) < 1e-4 and abs(d_o - 0.02873) < 1e-5
    assert np.allclose(dw_ho, [0.00804, 0.00556], atol=1e-5) and dw_ih.shape == (3, 2)
    assert pred.tolist() == [0, 1, 1, 0] and perdidas[-1] < 0.01
    print("\nTodas las comprobaciones pasaron. ¡La red multicapa resuelve XOR!")

    if "--graficar" in sys.argv:
        import matplotlib.pyplot as plt
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4))
        a1.plot(perdidas)
        a1.set_title("Curva de aprendizaje (XOR)")
        a1.set_xlabel("época")
        g = np.linspace(-0.5, 1.5, 200)
        gx, gy = np.meshgrid(g, g)
        _, Z = adelante(np.c_[gx.ravel(), gy.ravel()], *params)
        a2.contourf(gx, gy, Z.reshape(gx.shape), levels=[0, 0.5, 1], colors=["#C9D6EA", "#FBE3CF"])
        a2.scatter(X[:, 0], X[:, 1], c=y.ravel(), cmap="coolwarm", s=120, edgecolors="k")
        a2.set_title("Frontera aprendida: ya no es una recta")
        plt.tight_layout()
        plt.show()
