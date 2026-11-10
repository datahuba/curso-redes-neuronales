# Guía del notebook `1_05_descenso_por_gradiente_1D`: bajar por una parábola

**Puntos:** 2 · **Tiempo:** 15–20 min · **Clase:** 3 · **Archivo:** `notebooks/1_05_descenso_por_gradiente_1D.ipynb`
**Teoría completa:** [Guía de la Clase 3](../GUIA_PASO_A_PASO_CLASE3.md), sección B5.

## ¿Qué vas a aprender?
- A programar la regla del **descenso por gradiente**: x ← x − η·f′(x).
- A detener un ciclo cuando el resultado ya casi no cambia (**criterio de parada**).

## Antes de empezar
1. `conda activate nni`.
2. VS Code → **Open Folder** → `curso-redes-neuronales` → `notebooks/1_05_descenso_por_gradiente_1D.ipynb` → kernel **nni**.
3. El notebook guarda una gráfica en `notebooks/output/`. Esa carpeta ya viene en el repositorio; si no la tienes, haz `git pull` o créala.

## La idea en 2 minutos
- Queremos el x que hace **mínima** a f(x) = x². La respuesta es x = 0.
- La **derivada** f′(x) = 2x es la **pendiente**: indica hacia dónde sube la curva.
- Para bajar, damos un paso **en contra** de la pendiente: **x ← x − η·f′(x)**.
- **η** (tasa de aprendizaje) es el tamaño del paso.

## Paso a paso

### Celda: `f` y `df`
Define la función x² y su derivada 2x. Ejecútala.

### Celda `TODO`: `gradient_descent_update(theta, learning_rate)`
Devuelve el valor nuevo de theta con la regla de arriba. La derivada ya existe: es `df(theta)`.

### Celda "Prueba del método"
Empieza en x = 5 con tasa 0.1 y hace 5 pasos.

✅ **Comprobación:** `Historial de valores de x: [5, 4.0, 3.2, 2.56, 2.048, 1.6384]`. Puede mostrar más decimales, como 1.6384000000000003.

Cada paso multiplica x por 0.8, porque x − 0.1·2x = 0.8x. Por eso se acerca a 0 cada vez más despacio.

### Celda de la gráfica
Dibuja la parábola y los puntos rojos bajando hacia el fondo. También la guarda en `output/gradient_descent_1D.png`.

### Celda `TODO (1 punto)`: detenerse con un umbral
Reescribe el ciclo con `while` para que se detenga cuando "el error" sea menor que 0.001, y cuenta las iteraciones.

Pistas:
1. Empieza con `x = 5` y un contador `iteraciones = 0`.
2. Dentro del `while`: calcula el x nuevo, suma 1 al contador, y decide si ya paras.
3. Elige y escribe tu **criterio de parada**.

✅ **Comprobación** (ambos criterios son válidos si los explicas):

| Criterio | Iteraciones |
|---|---|
| El **cambio** \|x_nuevo − x\| < 0.001 | **32** (x final ≈ 0.00396) |
| El **valor** f(x) = x² < 0.001 | **23** |

## Para pensar
- ¿Qué pasa con tasa = 1.1? → Cada paso multiplica x por −1.2: oscila y **diverge**.
- ¿Y con 0.5? → Llega a 0 en un solo paso. Pasa solo en esta función tan simple.

## Errores frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `TypeError: unsupported operand ... NoneType` | `gradient_descent_update` devuelve `None` | Completa la función |
| `FileNotFoundError: output/gradient_descent_1D.png` | No existe la carpeta `output` | `git pull`, o crea la carpeta `notebooks/output` |
| El historial **crece** en lugar de bajar | Sumaste en vez de restar | Es `theta - learning_rate * df(theta)` |
| El `while` nunca termina | La condición nunca se cumple, o la tasa es muy grande | Revisa el criterio; detén la celda con el botón ■ |
