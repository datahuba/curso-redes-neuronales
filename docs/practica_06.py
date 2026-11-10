"""Clase 6: optimizadores. Descenso por gradiente en 2D, momentum y decaimiento de la tasa.

Ejecutar desde la carpeta del repo, con el ambiente nni activo:
    python docs/practica_06.py              -> tablas en la terminal
    python docs/practica_06.py --graficar   -> además dibuja los caminos sobre la función de Beale
"""
import math
import sys

import numpy as np


# --- funciones de prueba (las mismas del paquete nni) ---
def esfera(x, y):
    return x ** 2 + y ** 2


def grad_esfera(x, y):
    return [2 * x, 2 * y]


def beale(x, y):
    return (1.5 - x + x * y) ** 2 + (2.25 - x + x * y ** 2) ** 2 + (2.625 - x + x * y ** 3) ** 2


def grad_beale(x, y):
    a, b, c = 1.5 - x + x * y, 2.25 - x + x * y ** 2, 2.625 - x + x * y ** 3
    return [2 * a * (y - 1) + 2 * b * (y ** 2 - 1) + 2 * c * (y ** 3 - 1),
            2 * a * x + 2 * b * 2 * x * y + 2 * c * 3 * x * y ** 2]


# --- un optimizador genérico: recibe una regla de "paso" ---
def optimizar(f, grad, inicio, paso, max_iter=500, tol=1e-6):
    """Repite params <- paso(params, gradiente, t) hasta max_iter o hasta que casi no cambien."""
    params, camino = list(inicio), []
    for t in range(max_iter):
        camino.append(params)                        # igual que el historial de nni: un registro por iteración
        nuevos = paso(params, grad(*params), t)
        if not all(math.isfinite(v) and abs(v) < 1e6 for v in nuevos):
            return None, camino                      # diverge
        if all(abs(a - b) < tol for a, b in zip(params, nuevos)):
            break
        params = nuevos
    return params, camino


def descenso(eta):
    return lambda p, g, t: [a - eta * b for a, b in zip(p, g)]


def momentum(eta, beta):
    m = [0.0, 0.0]

    def paso(p, g, t):
        m[:] = [beta * mi + (1 - beta) * gi for mi, gi in zip(m, g)]
        return [a - eta * mi for a, mi in zip(p, m)]
    return paso


def decaimiento(eta0, regla):
    return lambda p, g, t: [a - regla(eta0, t) * b for a, b in zip(p, g)]


def escalonada(eta0, t, gamma=0.5, cada=100):
    return eta0 * gamma ** (t // cada)


def inversa(eta0, t, k=0.01):
    return eta0 / (1 + k * t)


def exponencial(eta0, t, k=0.01):
    return eta0 * math.exp(-k * t)


def texto(f, r):
    return "DIVERGE" if r is None else f"({r[0]:.3f}, {r[1]:.3f})  f = {f(*r):.2e}"


if __name__ == "__main__":
    print("1) Esfera f = x² + y², desde (-1, -1), máximo 300 iteraciones")
    res_esfera = {}
    for eta in [0.01, 0.1, 0.5, 0.9, 1.0]:
        r, camino = optimizar(esfera, grad_esfera, [-1, -1], descenso(eta), max_iter=300)
        res_esfera[eta] = len(camino)
        print(f"   eta = {eta:<4}  iteraciones = {len(camino):>3}   termina en ({r[0]:.4f}, {r[1]:.4f})")

    print("\n2) Beale desde (2.5, 1.0): descenso simple contra momentum (mínimo en (3, 0.5))")
    res_mom = {}
    for eta in [0.01, 0.03]:
        r, _ = optimizar(beale, grad_beale, [2.5, 1.0], descenso(eta))
        print(f"   eta = {eta}  descenso simple:   {texto(beale, r)}")
        for beta in [0.5, 0.9]:
            r, _ = optimizar(beale, grad_beale, [2.5, 1.0], momentum(eta, beta))
            res_mom[(eta, beta)] = r
            print(f"   eta = {eta}  momentum beta {beta}: {texto(beale, r)}")

    print("\n3) Beale desde (1.0, 1.0) con eta0 = 0.05: tasa fija contra decaimiento")
    res_dec = {}
    r, _ = optimizar(beale, grad_beale, [1.0, 1.0], descenso(0.05))
    res_dec["fija"] = r
    print(f"   {'fija 0.05':>12}: {texto(beale, r)}")
    for regla in [escalonada, inversa, exponencial]:
        r, _ = optimizar(beale, grad_beale, [1.0, 1.0], decaimiento(0.05, regla))
        res_dec[regla.__name__] = r
        print(f"   {regla.__name__:>12}: {texto(beale, r)}")

    # comprobaciones (los mismos números que dan los notebooks 21, 22 y 23)
    assert res_esfera[0.1] == 56 and res_esfera[0.5] == 2
    assert optimizar(beale, grad_beale, [2.5, 1.0], descenso(0.03))[0] is None
    assert beale(*res_mom[(0.03, 0.9)]) < 1e-5
    assert beale(*res_dec["fija"]) > 0.05 and beale(*res_dec["escalonada"]) < 1e-4
    print("\nTodas las comprobaciones pasaron.")

    if "--graficar" in sys.argv:
        import matplotlib.pyplot as plt
        gx, gy = np.meshgrid(np.linspace(0, 4.5, 200), np.linspace(-2, 2, 200))
        Z = np.log(beale(gx, gy) + 1)
        casos = [("Descenso, eta 0.01", [2.5, 1.0], descenso(0.01)),
                 ("Momentum, eta 0.03", [2.5, 1.0], momentum(0.03, 0.9)),
                 ("Fija 0.05", [1.0, 1.0], descenso(0.05)),
                 ("Decaimiento escalonado", [1.0, 1.0], decaimiento(0.05, escalonada))]
        fig, axs = plt.subplots(1, 4, figsize=(18, 4))
        for ax, (nombre, inicio, paso) in zip(axs, casos):
            _, camino = optimizar(beale, grad_beale, inicio, paso)
            c = np.array(camino)
            ax.contourf(gx, gy, Z, levels=60, cmap="viridis")
            ax.plot(c[:, 0], c[:, 1], "w.-", markersize=3)
            ax.plot(3, 0.5, "ro")
            ax.set_title(nombre)
        plt.tight_layout()
        plt.show()
