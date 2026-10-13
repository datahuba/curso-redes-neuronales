"""Módulo 2: neurona de McCulloch-Pitts y perceptrón (solo Python estándar)."""

# --- 2.3 McCulloch-Pitts ---
def mcculloch_pitts(x, umbral, inhibitorias=()):
    if any(x[i] for i in inhibitorias):
        return 0
    return 1 if sum(x) >= umbral else 0


# --- 2.5 Perceptrón ---
def escalon(z):
    return 1 if z >= 0 else 0


def predecir(x, w, b):
    return escalon(sum(wi * xi for wi, xi in zip(w, x)) + b)


def entrenar(X, y, eta=0.1, epocas=100):
    """Regla del perceptrón. Devuelve (w, b, épocas usadas, convergió)."""
    w, b = [0.0] * len(X[0]), 0.0
    for epoca in range(1, epocas + 1):
        errores = 0
        for xi, yi in zip(X, y):
            error = yi - predecir(xi, w, b)
            if error:
                errores += 1
                w = [wj + eta * error * xj for wj, xj in zip(w, xi)]
                b += eta * error
        if errores == 0:
            return w, b, epoca, True
    return w, b, epocas, False


if __name__ == "__main__":
    X = [(0, 0), (0, 1), (1, 0), (1, 1)]

    print("McCulloch-Pitts")
    for nombre, umbral, esperado in [("AND", 2, [0, 0, 0, 1]), ("OR", 1, [0, 1, 1, 1])]:
        salidas = [mcculloch_pitts(x, umbral) for x in X]
        assert salidas == esperado
        print(f"  {nombre} (umbral={umbral}): {salidas}")
    no = [mcculloch_pitts((x,), 0, inhibitorias=(0,)) for x in (0, 1)]
    assert no == [1, 0]
    print(f"  NOT: {no}")

    print("\nPerceptrón")
    for nombre, y in [("AND", [0, 0, 0, 1]), ("OR", [0, 1, 1, 1]), ("XOR", [0, 1, 1, 0])]:
        w, b, ep, ok = entrenar(X, y)
        salidas = [predecir(x, w, b) for x in X]
        print(f"  {nombre}: w={[round(v, 2) for v in w]} b={b:.2f} épocas={ep} "
              f"convergió={ok} salidas={salidas}")
        assert ok == (nombre != "XOR")  # XOR no es linealmente separable
    print("\nTodas las comprobaciones pasaron.")
