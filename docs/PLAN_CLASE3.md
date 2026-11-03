# Plan — Clase 3: Red neuronal simple (borrador)

**Estado:** propuesta para revisar antes de armar la guía y las diapositivas.
**Módulo del curso:** 3. Red neuronal simple (jivg.org, lecciones 3.1 a 3.14).
**Lecturas** (libro del Dr. Irving Vasquez):
- [Neurona artificial moderna](https://irvingvasquez.github.io/libro_redes_neuronales/chapters/03-fundamentos/04-neurona-artificial-moderna.html)
- [Descenso por gradiente (preliminares)](https://irvingvasquez.github.io/libro_redes_neuronales/chapters/02-preliminares/09-descenso-por-gradiente.html)
- [Descenso por gradiente (aprendizaje)](https://irvingvasquez.github.io/libro_redes_neuronales/chapters/04-aprendizaje/03-descenso-por-gradiente.html)

## Propuesta: partir el módulo 3 en dos clases

El módulo 3 es el más largo del curso (14 lecciones y 5 notebooks). En una sola sesión no cabe con práctica, así que propongo:

| Clase | Tema | Notebooks |
|---|---|---|
| **3** | Neurona moderna, funciones de activación y descenso por gradiente en 1D | `1_04_red_neuronal_simple`, `1_05_descenso_por_gradiente_1D` |
| **4** | Descenso por gradiente en una neurona (regla delta), entrenamiento completo, ADALINE, red con varias salidas e inicialización de pesos | `1_06_descenso_unpaso`, `1_07_descenso_por_gradiente`, `1_08_adaline` |

## Clase 3 — objetivos

Al terminar, cada alumno podrá:
1. Explicar en qué se diferencia la neurona moderna del perceptrón: la activación es **continua y derivable**.
2. Calcular y graficar las activaciones lineal, sigmoide, tanh y ReLU.
3. Aplicar a mano varias iteraciones del descenso por gradiente en una función de una variable.
4. Programar una neurona con sigmoide y el descenso por gradiente en Python.

## Clase 3 — contenido propuesto (~2 h 30 min)

| Tiempo | Tema | Idea central y ejemplo verificado |
|---|---|---|
| 0:00 | Repaso de la Clase 2 | El perceptrón solo separa con una recta; su escalón no tiene derivada útil. |
| 0:10 | **Neurona artificial moderna** (Widrow y Hoff, 1960: ADALINE) | El escalón se cambia por una función continua y derivable, lo que permite entrenar con gradiente. |
| 0:25 | **Funciones de activación** | Lineal f(h) = h · sigmoide 1/(1+e⁻ʰ), rango 0 a 1, se satura · tanh, rango −1 a 1 · ReLU = máx(0, h). Gráficas de las cuatro. |
| 0:45 | Ejemplo a mano | Entradas [0.7, −0.3], pesos [0.1, 0.8], sesgo −0.1 → h = −0.27 → **sigmoide ≈ 0.4329** · tanh ≈ −0.2636. Son los mismos números del notebook `1_04`. |
| 0:55 | **Práctica `1_04_red_neuronal_simple`** (3 pts) | `sigmoide`, clase `Neurona` (combinación lineal y forward), tanh y comparación con la sigmoide. |
| 1:20 | Descanso | |
| 1:30 | **Descenso por gradiente: la intuición** | Bajar una montaña a oscuras sintiendo la pendiente con los pies. Regla: x ← x − η·f′(x). |
| 1:45 | Ejemplo a mano | f(x) = x², f′(x) = 2x, η = 0.1. Desde x = −2: **−1.6**. Desde x = 5: **5 → 4 → 3.2 → 2.56 → 2.048 → 1.6384**. Ejercicio: f(x) = 2x + x², x₀ = 10, η = 0.2. |
| 2:00 | **Práctica `1_05_descenso_por_gradiente_1D`** (2 pts) | `gradient_descent_update`; detener cuando el cambio sea menor que 10⁻³ y contar las iteraciones. |
| 2:20 | Cierre y tarea | Avance de la Clase 4: aplicar el descenso a los pesos de una neurona. |

## Ejemplos ya verificados para la Clase 4
- **Un paso de la regla delta** (notebook `1_06`): x = [1, 1], y = 1, w = [0.1, 0.2], b = 0, η = 2.
  - h = 0.3, ŷ ≈ 0.5744.
  - δ = (y − ŷ)·ŷ(1 − ŷ) ≈ 0.1040.
  - Δw ≈ [0.2081, 0.2081], Δb ≈ 0.2081.
  - Después del paso: ŷ ≈ 0.7159 y la pérdida baja de 0.0905 a 0.0404.
- **Red con varias salidas** (libro, cap. 21): X = [8, 4], W = [[−0.1, 0.6], [−0.8, 0.3]], B = [−0.7, 0.3].
  - Resultado: H = XW + B = **[−4.7, 6.3]**, ŷ ≈ [0.0090, 0.9982].
  - ⚠️ El libro trae **H = [−7.7, 6.3]** y ŷ = [4.52·10⁻⁴, 9.81·10⁻¹]: parece un error de cuentas, porque 8·(−0.1) + 4·(−0.8) − 0.7 = −4.7. Conviene usar los valores corregidos en clase (o señalarlo como ejercicio de "encuentra el error").

## Decisiones pendientes
1. ¿Partimos el módulo 3 en dos clases (3 y 4) como se propone, o lo condensamos en una sola sesión larga?
2. ¿Agregamos una práctica propia en Python puro (como `docs/practica_02.py`), que grafique las cuatro activaciones y el descenso en x²?
3. Fecha de la clase, para calcular cuánto tiempo hay para preparar el material.
