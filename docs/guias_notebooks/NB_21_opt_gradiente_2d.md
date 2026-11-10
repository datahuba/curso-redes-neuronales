# Guía del notebook `21_opt_gradiente_2d`: descenso por gradiente en dos dimensiones

**Puntos:** experimentos, sin `TODO` · **Tiempo:** 20 min · **Módulo:** optimización (clase 6) · **Archivo:** `notebooks/21_opt_gradiente_2d.ipynb`
**Requisito:** `1_05` (descenso por gradiente en una variable).

## ¿Qué vas a aprender?
- A extender el descenso por gradiente a **dos parámetros** a la vez.
- A leer un **mapa de contorno**, que es como un mapa topográfico de la función.
- A ver con tus propios ojos el efecto de la tasa de aprendizaje.

## Antes de empezar
1. `conda activate nni`.
2. VS Code → **Open Folder** → `curso-redes-neuronales` → `notebooks/21_opt_gradiente_2d.ipynb` → kernel **nni**.
3. Ejecuta las celdas en orden con **Shift + Enter**.

## La idea en 2 minutos
- **Función esférica:** f(x, y) = x² + y². Es un "tazón" cuyo fondo está en (0, 0).
- **Gradiente:** con dos variables hay una derivada por cada una (**derivadas parciales**):
  - ∂f/∂x = 2x, que se calcula como si y fuera un número fijo;
  - ∂f/∂y = 2y.
  - Juntas forman el **gradiente** ∇f = (2x, 2y): una flecha que apunta hacia donde la función sube más rápido.
- **Regla:** igual que en 1D, pero para cada parámetro: x ← x − η·∂f/∂x y y ← y − η·∂f/∂y.
- **Contorno:** cada color es una "altura". El punto rojo es el mínimo; la línea blanca, el camino del descenso.

## Recorrido por las celdas
1. **Paquetes y el problema:** `nni.SphereProblem()` trae la función, sus derivadas y el área a dibujar (de −2 a 2).
2. **Gráficas:** el mapa de contorno (izquierda) y la superficie 3D (derecha).
3. **Clase `GradientDescentOptimizer`** (léela con calma):
   - `next_params`: aplica la regla a cada parámetro;
   - `optimize`: repite hasta llegar al máximo de iteraciones o hasta que los parámetros casi no cambien (`tolerance`);
   - `history`: guarda cada paso para dibujarlo.
4. **Hiperparámetros:** inicio (−1, −1), tasa 0.01 y 300 iteraciones.
5. **Optimizar.**
   ✅ **Comprobación:** con los valores originales, `Parámetros optimizados` ≈ **[−0.00233, −0.00233]** y `Mejor valor encontrado` ≈ **1.09·10⁻⁵**. Usa las 300 iteraciones: con 0.01 avanza lento.
6. **Camino en el contorno:** una línea recta desde (−1, −1) hacia el centro.
7. **Animación:** guarda un video `gradient_descent.mp4`.

> ⚠️ El video **necesita ffmpeg**. Si sale `RuntimeError: Requested MovieWriter (ffmpeg) not available`, cambia el final de esa línea por `.save('gradient_descent.gif', writer='pillow')`. Así guarda un GIF sin instalar nada más.

## Experimentos sugeridos
Cambia `learning_rate` en la celda de hiperparámetros y vuelve a ejecutar desde ahí. Resultados reales desde (−1, −1), con un máximo de 300 iteraciones:

| Tasa | Iteraciones | Dónde termina | Qué pasa |
|---|---|---|---|
| 0.01 | 300 (el máximo) | (−0.0023, −0.0023) | Lento: no termina de llegar |
| 0.1 | 56 | (0, 0) | Bien |
| 0.5 | 2 | (0, 0) | Llega de un salto (solo en esta función) |
| 0.9 | 66 | (0, 0) | Llega, pero **zigzagueando** de un lado al otro |
| 1.0 | 300 | (−1, −1) | **Rebota para siempre** entre (−1, −1) y (1, 1) |
| > 1.0 | — | se aleja | **Diverge** |

**¿Por qué?** Cada paso multiplica x por (1 − 2η):
- con η = 0.9, ese factor es −0.8: cambia de signo, pero se achica;
- con η = 1, es −1: cambia de signo sin achicarse nunca;
- con η > 1, crece en cada paso.

## Para pensar
- Cambia el punto inicial a (2, −1.5). ¿El camino sigue siendo una recta? (En la esfera, sí.)
- ¿Qué pasaría en una función con forma de valle alargado, en lugar de un tazón redondo? Lo verás en el notebook 22.

## Errores frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `RuntimeError: ... MovieWriter (ffmpeg) not available` | No hay ffmpeg | Guarda como GIF con `writer='pillow'`, o salta esa celda |
| Aviso `Locator attempting to generate 1001 ticks` | `levels=1000` en el contorno | Solo es un aviso; puedes bajar a `levels=100` |
| `AttributeError: module 'nni' has no attribute 'SphereProblem'` | Notebook abierto fuera del repo, o `nni` viejo | Abre la carpeta `curso-redes-neuronales` y haz `git pull` |
| `OverflowError` | Tasa > 1: los números crecen sin límite | Usa una tasa menor que 1 |
