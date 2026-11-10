"""Clase 7: la operación de una capa convolucional y cómo se aprende un kernel.

Ejecutar desde la carpeta del repo, con el ambiente nni activo:
    python docs/practica_07.py              -> resultados en la terminal
    python docs/practica_07.py --graficar   -> además muestra las imágenes
"""
import os
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))


def correlacion(I, K):
    """Correlación cruzada 'válida' (sin padding), vectorizada: suma de versiones desplazadas de I."""
    k = K.shape[0] // 2
    m, n = I.shape
    G = np.zeros((m - 2 * k, n - 2 * k))
    for u in range(-k, k + 1):
        for v in range(-k, k + 1):
            G += K[u + k, v + k] * I[k + u:m - k + u, k + v:n - k + v]
    return G


def correlacion_a_mano(I, K, i, j):
    """Un solo píxel, con dos for: como en el pizarrón."""
    k = K.shape[0] // 2
    return sum(K[u + k, v + k] * I[i + u, j + v] for u in range(-k, k + 1) for v in range(-k, k + 1))


def aprender_kernel(I, T, tam=3, eta=0.5, epocas=300, semilla=0):
    """Descenso por gradiente sobre los números del kernel (sin ReLU) para que correlacion(I, K) ≈ T."""
    k = tam // 2
    m, n = I.shape
    despl = {(u, v): I[k + u:m - k + u, k + v:n - k + v] for u in range(-k, k + 1) for v in range(-k, k + 1)}
    K = np.random.default_rng(semilla).normal(0, 0.1, size=(tam, tam))
    ecm = []
    for _ in range(epocas):
        P = correlacion(I, K)
        E = P - T
        ecm.append(float(np.mean(E ** 2)))
        grad = np.array([[2 * np.mean(E * despl[(u, v)]) for v in range(-k, k + 1)] for u in range(-k, k + 1)])
        K -= eta * grad
    return K, ecm


if __name__ == "__main__":
    print("1) Ejemplo del pizarrón: imagen 5x5 (oscuro a la izquierda, claro a la derecha)")
    I = np.array([[0, 0, 9, 9, 9]] * 5, dtype=float)
    K = np.array([[-1, 0, 1]] * 3, dtype=float)          # detector de bordes verticales
    G = correlacion(I, K)
    print("   salida (3x3):")
    print("  ", G.astype(int).tolist())
    print(f"   un píxel a mano, centro (1, 1): {correlacion_a_mano(I, K, 1, 1):.0f}")

    print("\n2) Aprender el kernel: la salida objetivo se hizo con Sobel; ¿lo descubre el descenso?")
    rng = np.random.default_rng(1)
    img = rng.random((40, 40)) - 0.5                     # imagen de ruido centrada en 0 (sin centrar, diverge)
    sobel = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=float)
    T = correlacion(img, sobel)
    K_apr, ecm = aprender_kernel(img, T)
    print(f"   ECM: {ecm[0]:.4f} -> {ecm[-1]:.6f}")
    print("   kernel aprendido:")
    print("  ", np.round(K_apr, 2).tolist())

    # comprobaciones
    assert G.tolist() == [[27, 27, 0]] * 3 and correlacion_a_mano(I, K, 1, 1) == 27
    assert np.allclose(K_apr, sobel, atol=0.05) and ecm[-1] < 1e-3
    print("\nTodas las comprobaciones pasaron: el descenso por gradiente encontró el filtro de Sobel.")

    if "--graficar" in sys.argv:
        import matplotlib.pyplot as plt
        from PIL import Image
        lenna = np.array(Image.open(os.path.join(AQUI, "..", "notebooks", "files", "Lenna.png")))[:, :, 0] / 255
        fig, axs = plt.subplots(1, 4, figsize=(17, 4))
        axs[0].imshow(lenna, cmap="gray")
        axs[0].set_title("Original (canal rojo)")
        axs[1].imshow(np.maximum(0, correlacion(lenna, np.array([[-1, 0, 1]] * 3) / 3)), cmap="gray")
        axs[1].set_title("Bordes verticales + ReLU")
        axs[2].imshow(np.maximum(0, correlacion(lenna, sobel)), cmap="gray")
        axs[2].set_title("Sobel (bordes horizontales) + ReLU")
        axs[3].plot(ecm)
        axs[3].set_yscale("log")
        axs[3].set_title("ECM al aprender el kernel")
        plt.tight_layout()
        plt.show()
