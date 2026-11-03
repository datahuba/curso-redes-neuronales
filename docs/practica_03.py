"""Clase 3: funciones de activación y descenso por gradiente en una variable.

Ejecutar desde la carpeta del repo, con el ambiente nni activo:
    python docs/practica_03.py              -> tablas en la terminal
    python docs/practica_03.py --graficar   -> además muestra las gráficas
"""
import sys

import numpy as np


# --- Funciones de activación y sus derivadas (pendientes) ---
def lineal(h):
    return h


def sigmoide(h):
    return 1 / (1 + np.exp(-h))


def tanh(h):
    return np.tanh(h)


def relu(h):
    return np.maximum(0, h)


def sigmoide_prima(h):
    return sigmoide(h) * (1 - sigmoide(h))


ACTIVACIONES = {"lineal": lineal, "sigmoide": sigmoide, "tanh": tanh, "ReLU": relu}


# --- Descenso por gradiente en una variable: x <- x - eta * f'(x) ---
def descenso(df, x0, eta, pasos):
    xs = [x0]
    for _ in range(pasos):
        xs.append(xs[-1] - eta * df(xs[-1]))
    return xs


def tabla_activaciones():
    print("Funciones de activación")
    print(f"{'h':>5} | {'lineal':>7} {'sigmoide':>9} {'tanh':>8} {'ReLU':>6} | {'sigmoide_prima':>14}")
    for h in [-3, -1, 0, 1, 3]:
        fila = " ".join(f"{float(f(h)):>{w}.4f}" for f, w in zip(ACTIVACIONES.values(), (7, 9, 8, 6)))
        print(f"{h:>5} | {fila} | {sigmoide_prima(h):>14.4f}")


def ejemplo_neurona():
    x, w, b = np.array([0.7, -0.3]), np.array([0.1, 0.8]), -0.1
    h = np.dot(w, x) + b
    print(f"\nNeurona del notebook 1_04: h = {h:.2f} -> sigmoide = {sigmoide(h):.4f}, tanh = {tanh(h):.4f}")
    return h


def ejemplos_descenso():
    print("\nDescenso por gradiente en f(x) = x^2   (f'(x) = 2x)")
    for eta in [0.01, 0.1, 0.5, 0.9, 1.1]:
        xs = descenso(lambda x: 2 * x, 5.0, eta, 5)
        print(f"  eta = {eta:<4}: " + " -> ".join(f"{v:.3f}" for v in xs))
    print("  0.01 avanza lento · 0.1 bien · 0.5 llega de un salto · 0.9 oscila · 1.1 se aleja (diverge)")
    xs = descenso(lambda x: 2 + 2 * x, 10.0, 0.2, 6)
    print("\nEjercicio del libro: f(x) = 2x + x^2, x0 = 10, eta = 0.2 (mínimo en x = -1)")
    print("  " + " -> ".join(f"{v:.4f}" for v in xs))
    return xs


def graficar():
    import matplotlib.pyplot as plt
    h = np.linspace(-5, 5, 200)
    fig, ejes = plt.subplots(1, 4, figsize=(14, 3.2))
    for ax, (nombre, f) in zip(ejes, ACTIVACIONES.items()):
        ax.plot(h, f(h), lw=2.5)
        ax.axhline(0, color="gray", lw=0.6)
        ax.axvline(0, color="gray", lw=0.6)
        ax.set_title(nombre)
    plt.tight_layout()
    xs = np.array(descenso(lambda x: 2 * x, 5.0, 0.1, 10))
    t = np.linspace(-6, 6, 200)
    plt.figure(figsize=(6, 4))
    plt.plot(t, t ** 2, label="f(x) = x²")
    plt.plot(xs, xs ** 2, "o-", color="tab:orange", label="pasos del descenso (η = 0.1)")
    plt.legend()
    plt.title("Descenso por gradiente")
    plt.show()


if __name__ == "__main__":
    tabla_activaciones()
    h = ejemplo_neurona()
    xs = ejemplos_descenso()
    # comprobaciones
    assert abs(sigmoide(0) - 0.5) < 1e-12 and abs(sigmoide_prima(0) - 0.25) < 1e-12
    assert abs(sigmoide(h) - 0.4329) < 1e-4
    assert np.allclose(descenso(lambda x: 2 * x, 5.0, 0.1, 5), [5, 4, 3.2, 2.56, 2.048, 1.6384])
    assert abs(descenso(lambda x: 2 * x, -2.0, 0.1, 1)[1] - (-1.6)) < 1e-12
    assert abs(xs[-1] - (-0.48678)) < 1e-4
    print("\nTodas las comprobaciones pasaron.")
    if "--graficar" in sys.argv:
        graficar()
