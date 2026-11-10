# Guía del notebook `1_02_perceptron_AND`: pesos a mano para AND

**Puntos:** práctica, sin puntos · **Tiempo:** 5–10 min · **Clase:** 2 · **Archivo:** `notebooks/1_02_perceptron_AND.ipynb`
**Teoría completa:** [Guía de la Clase 2](../GUIA_PASO_A_PASO_CLASE2.md), sección B3.

## ¿Qué vas a aprender?
- Que un perceptrón es una **recta** que separa dos grupos de puntos.
- A elegir pesos y sesgo **a mano** para que el perceptrón calcule la compuerta AND.

## Antes de empezar
1. `conda activate nni` en Anaconda PowerShell Prompt.
2. VS Code → **Open Folder** → `curso-redes-neuronales` → `notebooks/1_02_perceptron_AND.ipynb` → kernel **nni**.
3. Ejecuta las celdas en orden con **Shift + Enter**.

## La idea en 2 minutos
El perceptrón calcula:

1. **Combinación lineal:** h = peso1·x₁ + peso2·x₂ + sesgo
2. **Activación escalón:** salida = 1 si h ≥ 0, y 0 si h < 0.

**AND** vale 1 **solo** cuando las dos entradas son 1:

| x₁ | x₂ | AND |
|---|---|---|
| 0 | 0 | 0 |
| 0 | 1 | 0 |
| 1 | 0 | 0 |
| 1 | 1 | 1 |

Necesitas que h sea **negativa** en los tres primeros casos y **positiva o cero** en el último.

## Paso a paso

### Celda `TODO`: `weight1`, `weight2` y `bias`
Cambia los tres valores (que empiezan en 0).

Pistas para razonar:
- Con los dos pesos iguales y positivos, el caso (1, 1) da la suma más grande.
- El sesgo debe ser negativo: lo bastante para "apagar" los casos con un solo 1, pero no tanto como para apagar el caso (1, 1).
- Prueba pesos de 1 y busca el sesgo entre −1 y −2.

### Celda "ESTO DEBE QUEDAR IGUAL"
**No la modifiques.** Prueba tus pesos con las 4 entradas y te dice cuántas acertaste.

✅ **Comprobación:** debe decir `Bien!  Acertaste todas.` y la columna `Is Correct` debe decir `Yes` en las cuatro filas. Por ejemplo, una solución válida da combinaciones lineales −1.5, −0.5, −0.5 y 0.5.

> Hay **muchas** soluciones correctas: cualquier recta que deje solo el punto (1, 1) del lado positivo.

## Para pensar
- ¿Qué cambiarías para que calcule **OR** (1 si al menos una entrada es 1)? → Solo el sesgo, menos negativo.
- ¿Y NAND (lo contrario de AND)? → Todos los signos al revés.

## Errores frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `Obtuvieste 1 mal` en la fila (1, 1) | El sesgo es demasiado negativo | Súbelo un poco (hazlo menos negativo) |
| Fallan las filas (0, 1) y (1, 0) | El sesgo no es lo bastante negativo | Bájalo |
| `NameError: weight1` | No ejecutaste la celda de los pesos | Ejecútala antes que la de prueba |
