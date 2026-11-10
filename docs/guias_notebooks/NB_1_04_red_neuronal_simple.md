# Guía del notebook `1_04_red_neuronal_simple`: una neurona con sigmoide

**Puntos:** 3 · **Tiempo:** 20 min · **Clase:** 3 · **Archivo:** `notebooks/1_04_red_neuronal_simple.ipynb`
**Teoría completa:** [Guía de la Clase 3](../GUIA_PASO_A_PASO_CLASE3.md), secciones B1 a B4.

## ¿Qué vas a aprender?
- A programar la función **sigmoide**, un "escalón suave".
- A escribir una neurona como una **clase** de Python, con sus métodos.
- A comparar la sigmoide con la **tangente hiperbólica (tanh)**.

## Antes de empezar
1. `conda activate nni`.
2. VS Code → **Open Folder** → `curso-redes-neuronales` → `notebooks/1_04_red_neuronal_simple.ipynb` → kernel **nni**.
3. Ejecuta las celdas en orden con **Shift + Enter**.

## La idea en 2 minutos
- La neurona moderna hace lo mismo que el perceptrón: h = W·X + b y luego ŷ = f(h). Pero **f es suave**.
- **Sigmoide:** σ(h) = 1 / (1 + e⁻ʰ). Devuelve un número entre 0 y 1.
- **tanh:** (eʰ − e⁻ʰ) / (eʰ + e⁻ʰ). Devuelve un número entre −1 y 1.
- En NumPy, eˣ se escribe `np.exp(x)`, y el producto punto W·X se escribe `np.dot(W, X)`.

## Paso a paso

### Celda "Cargamos paquetes"
Ejecútala.

### Celda `TODO (1 punto)`: `sigmoide(h)`
Escribe la fórmula y devuelve el resultado.
⚠️ Ojo con el **signo menos** del exponente: es `np.exp(-h)`.

### Celda `TODO (1 punto)`: clase `Neurona`
Completa los dos métodos:
- **`combinacion_lineal(self, X)`:** devuelve h = W·X + b. Usa `np.dot(self.W, X) + self.b`. Dentro de la clase, los pesos se llaman `self.W` y el sesgo `self.b`.
- **`forward(self, X)`:** calcula h llamando a `self.combinacion_lineal(X)` y devuelve `self.activacion(h)`.

### Celda "Definamos unos pesos y sesgo"
Usa entradas [0.7, −0.3], pesos [0.1, 0.8] y sesgo −0.1.

✅ **Comprobación:** debe imprimir **`Output: 0.4329`**.
- La cuenta: h = 0.07 − 0.24 − 0.1 = −0.27, y σ(−0.27) = 1 / (1 + e⁰·²⁷) = 1 / 2.3100 ≈ 0.4329.
- Si te da **0.5671**, te falta el signo menos en `np.exp(-h)`.

### Celda `TODO (1 punto)`: tanh y comparación
1. Escribe una función `tanh(h)` con la fórmula de arriba.
2. Crea otra neurona con los mismos pesos, sesgo y entradas, pero con `tanh` como activación.
3. Imprime las dos salidas.

✅ **Comprobación:**
- con tanh sale **−0.2636**, y con la sigmoide **0.4329**;
- puedes comparar tu tanh con `np.tanh(-0.27)`, que también da −0.2636.

**Para comentar:** tanh es negativa porque h < 0; la sigmoide nunca es negativa (vale entre 0 y 1).

## Errores frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `TypeError: unsupported format string passed to NoneType` | Una función o método devuelve `None` | Completa el `TODO` y ejecuta de nuevo esa celda **y** la de prueba |
| Da 0.5671 | Falta el signo: `np.exp(h)` | Debe ser `np.exp(-h)` |
| `NameError: name 'W' is not defined` | Dentro de la clase escribiste `W` | Usa `self.W` y `self.b` |
| `ValueError: shapes not aligned` | Pesos y entradas de distinto tamaño | Ambos deben tener 2 elementos |
