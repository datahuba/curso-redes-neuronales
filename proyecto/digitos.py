"""Herramientas del proyecto «Reconocedor de dígitos».

Aquí está lo aburrido (descargar datos, dibujar, guardar) para que en clase nos concentremos en la red.
"""
import os
import urllib.request

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
URL_MNIST = "https://storage.googleapis.com/tensorflow/tf-keras-datasets/mnist.npz"


def cargar_mnist():
    """Devuelve (X_train, y_train, X_test, y_test).

    X_*: imágenes de 28x28 con valores de 0 (negro) a 255 (blanco).  y_*: el dígito correcto (0..9).
    La primera vez descarga ~11 MB a proyecto/datos/mnist.npz; después lo lee del disco.
    """
    ruta = os.path.join(AQUI, "datos", "mnist.npz")
    if not os.path.exists(ruta):
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        print("Descargando MNIST (11 MB)... solo la primera vez")
        urllib.request.urlretrieve(URL_MNIST, ruta)
    d = np.load(ruta)
    return d["x_train"], d["y_train"], d["x_test"], d["y_test"]


def mostrar(imagenes, titulos=None, columnas=10):
    """Dibuja una o varias imágenes de 28x28 (o vectores de 784)."""
    import matplotlib.pyplot as plt

    imagenes = np.asarray(imagenes, dtype=float)
    if imagenes.ndim == 1 or imagenes.shape == (28, 28):
        imagenes = imagenes[None]
    imagenes = imagenes.reshape(len(imagenes), 28, 28)
    n = len(imagenes)
    columnas = min(columnas, n)
    filas = (n + columnas - 1) // columnas
    fig, ejes = plt.subplots(filas, columnas, figsize=(1.3 * columnas, 1.5 * filas), squeeze=False)
    for i, ax in enumerate(ejes.flat):
        ax.axis("off")
        if i < n:
            ax.imshow(imagenes[i], cmap="gray")
            if titulos is not None:
                ax.set_title(str(titulos[i]), fontsize=11)
    plt.tight_layout()
    plt.show()


def ok(condicion, mensaje):
    """Comprobación para los ejercicios: ✅ si está bien, ❌ con una pista si no."""
    if condicion:
        print("✅", mensaje)
    else:
        raise AssertionError("❌ Todavía no: " + mensaje)


def guardar_pesos(nombre="pesos.npz", **pesos):
    """Guarda los pesos de la red: guardar_pesos(W1=W1, b1=b1, W2=W2, b2=b2)."""
    np.savez(os.path.join(AQUI, nombre), **pesos)
    print("Pesos guardados en", nombre, "→ ahora prueba:  python dibujar.py")


def predecir_con_pesos(pesos, x):
    """Red densa genérica: capas W1,b1, W2,b2, ... con ReLU en medio y softmax al final.

    x: vector(es) de 784 valores entre 0 y 1.  Devuelve las probabilidades de cada dígito.
    """
    a = np.atleast_2d(x)
    n_capas = sum(1 for k in pesos if k.startswith("W"))
    for i in range(1, n_capas + 1):
        a = a @ pesos[f"W{i}"] + pesos[f"b{i}"]
        if i < n_capas:
            a = np.maximum(0, a)
    a = np.exp(a - a.max(axis=1, keepdims=True))
    return a / a.sum(axis=1, keepdims=True)


def preparar_dibujo(img):
    """Convierte un dibujo (fondo negro, trazo blanco, cualquier tamaño) al formato de MNIST.

    MNIST mete cada dígito en una caja de 20x20 y lo centra por su «centro de masa» en 28x28.
    Si no hacemos lo mismo, la red ve algo distinto a lo que aprendió y se equivoca.
    """
    from PIL import Image

    a = np.asarray(img, dtype=float)
    if a.ndim == 3:
        a = a[..., :3].mean(axis=2)
    if a.mean() > 127:            # fondo blanco (Paint): invertir
        a = 255 - a
    filas = np.where(a.max(axis=1) > 30)[0]
    cols = np.where(a.max(axis=0) > 30)[0]
    if len(filas) == 0:
        return np.zeros(784)
    a = a[filas[0]:filas[-1] + 1, cols[0]:cols[-1] + 1]
    escala = 20 / max(a.shape)
    nuevo = (max(1, round(a.shape[1] * escala)), max(1, round(a.shape[0] * escala)))
    a = np.asarray(Image.fromarray(a.astype(np.uint8)).resize(nuevo, Image.LANCZOS), dtype=float)
    lienzo = np.zeros((28, 28))
    y0, x0 = (28 - a.shape[0]) // 2, (28 - a.shape[1]) // 2
    lienzo[y0:y0 + a.shape[0], x0:x0 + a.shape[1]] = a
    total = lienzo.sum()
    if total > 0:                  # mover el centro de masa al centro (14, 14)
        yy, xx = np.indices(lienzo.shape)
        dy = int(round(14 - (yy * lienzo).sum() / total))
        dx = int(round(14 - (xx * lienzo).sum() / total))
        lienzo = np.roll(lienzo, (dy, dx), axis=(0, 1))
    return (lienzo / 255).reshape(784)


def leer_dibujo(ruta):
    """Lee un PNG dibujado en Paint (o en el celular) y lo deja listo para la red."""
    from PIL import Image

    return preparar_dibujo(Image.open(ruta).convert("L"))


if __name__ == "__main__":
    X, y, Xt, yt = cargar_mnist()
    assert X.shape == (60000, 28, 28) and Xt.shape == (10000, 28, 28)
    # un dígito de MNIST pasado por preparar_dibujo debe quedar casi igual
    x = preparar_dibujo(X[0])
    assert x.shape == (784,) and 0 <= x.min() and x.max() <= 1
    assert np.corrcoef(x, X[0].reshape(784) / 255)[0, 1] > 0.6
    p = predecir_con_pesos({"W1": np.zeros((784, 10)), "b1": np.zeros(10)}, x)
    assert np.allclose(p, 0.1)
    print("digitos.py OK")
