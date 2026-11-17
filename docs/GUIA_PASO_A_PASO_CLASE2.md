# Guía paso a paso — Clase 2: Una neurona que aprende de sus errores

**Proyecto:** reconocedor de dígitos escritos a mano, en Python y NumPy.
**Pieza de hoy:** una neurona (el perceptrón) que distingue el 0 del 1 con **99.8 %** de aciertos y corrige sus pesos cada vez que se equivoca.
**Problema que resolvemos:** las plantillas de la Clase 1 nunca cambian; si se equivocan, no aprenden nada.
**Duración:** ~2 h de clase, más 15–30 min de margen para dudas
**Material:** diapositivas `Clase2_Diapositivas` · notebook `proyecto/P2_una_neurona.ipynb` · repositorio https://github.com/datahuba/curso-redes-neuronales
**Lectura opcional** (libro del Dr. Irving Vasquez): [Neurona de McCulloch y Pitts y perceptrón](https://irvingvasquez.github.io/libro_redes_neuronales/)

## Objetivos de la clase

Al terminar, cada alumno podrá:
1. Explicar qué hace una neurona artificial: **suma ponderada + decisión**.
2. Programar una neurona y encontrar a mano los pesos de una compuerta AND.
3. Aplicar la **regla de aprendizaje de Rosenblatt** y entrenar una neurona con imágenes reales.
4. Interpretar los pesos aprendidos como una imagen.

## Agenda

> **Cómo se da esta clase:** directo a la práctica. Los alumnos abren el notebook en el minuto 2 y la teoría entra en **pausas cortas** (⏸) justo cuando el ejercicio la necesita. Regla de oro: **primero lo hacen, después lo explicas** (o, si hace falta para poder hacerlo, lo explicas en 3–5 minutos y vuelven al teclado). Las diapositivas siguen el mismo orden: «Paso» (oscuras) = trabajan; «Pausa · teoría» (claras) = explicas.

| Tiempo | Qué pasa |
|---|---|
| 0:00 | Abrir `P2` y la misión de hoy (3 min) |
| 0:03 | **Paso 1** · Compuerta AND a mano (12 min) |
| 0:15 | ⏸ Pausa: lo que construiste es una neurona (5 min) |
| 0:20 | **Paso 2** · La neurona con imágenes (20 min) |
| 0:40 | Descanso (10 min) |
| 0:50 | ⏸ Pausa: la regla de Rosenblatt, con un ejemplo en el pizarrón (8 min) |
| 0:58 | **Paso 3** · Entrenar y mirar los pesos (30 min) |
| 1:28 | **Paso 4** · Desafío 3 vs 5 (25 min) |
| 1:53 | Puesta en común, mapa y cierre (12 min) |

---

# PARTE A — Antes de clase (10 min)

En **Anaconda PowerShell Prompt**:

```bash
cd ~\projects\curso-redes-neuronales
```
```bash
git pull
```
```bash
conda activate nni
```

**Docente:** ejecuta completo `notebooks_resueltos/proyecto/P2_una_neurona.ipynb` (si no existe: `python tools/build_proyecto.py`). Así tienes a mano los resultados esperados y la imagen de los pesos para mostrar.

**Checklist:**
- [ ] `git pull` trajo `proyecto/P2_una_neurona.ipynb`.
- [ ] El notebook abre con el kernel **nni** y la primera celda corre sin errores.
- [ ] Tienes el resuelto ejecutado.

---

# PARTE B — La clase paso a paso

## Arranque (3 min)
Diapositiva «Manos al teclado». Mientras abren `proyecto/P2_una_neurona.ipynb`, di la misión: *hoy una neurona que distingue el 0 del 1 y aprende de sus errores, porque las plantillas no aprendían nada.*

## Paso 1 · Compuerta AND a mano (12 min)
**Haz:** sección 1. Buscar `w` y `b` para que solo `[1, 1]` dé 1. **Sin explicación previa**: que prueben números.
**Deben ver:** `✅ tu neurona es una compuerta AND`. Una solución: pesos `1, 1` y sesgo `-1.5`.
**Si se traban (5 min):** *prueba pesos 1 y 1; ¿cuánto suman las entradas en cada caso? ¿Qué sesgo deja pasar solo el 2?*

## ⏸ Pausa: lo que construiste es una neurona (5 min)
Explica **sobre lo que acaban de hacer**:
- **Pesos:** cuánto importa cada entrada (pueden ser negativos). **Sesgo:** qué tan fácil es decir que sí. **Decide:** 1 si `x @ w + b > 0`.
- `@` multiplica casilla por casilla y suma: con una imagen son 784 multiplicaciones en una línea.
- *¿Y la compuerta OR?* (sesgo −0.5). *¿Hay una sola respuesta?* No, infinitas → **se puede aprender**.
- Historia en 30 s: McCulloch y Pitts (1943) con pesos fijos; Rosenblatt (1958) los aprende.

## Paso 2 · La neurona con imágenes (20 min)
**Haz:** sección 2 y Ejercicio 1: `neurona(x, w, b)` con `(x @ w + b > 0).astype(int)`.
**Deben ver:** precisión con pesos al azar ~50 % (como tirar una moneda).
**Error típico:** usar `if`, que funciona con una imagen y falla con muchas.

## Descanso (10 min)

## ⏸ Pausa: la regla de Rosenblatt (8 min)
En el pizarrón, «imagen» de 3 píxeles `x = [1, 0, 1]`, `w = [0, 0, 0]`, `b = 0`, `η = 0.1`, correcta `y = 1`:
1. Suma 0 → dice 0 → error `= 1 − 0 = +1`.
2. `w ← w + η·error·x = [0.1, 0, 0.1]`, `b = 0.1`.
3. Próxima vez: suma 0.3 > 0 → dice 1 ✅.

**Intuición:** solo cambian los pesos de los píxeles **encendidos**, en la dirección que habría evitado el error. Si acierta, no cambia nada. Y directo al Paso 3.

## Paso 3 · Entrenar y mirar los pesos (30 min)
**Haz:** Ejercicio 2 (las dos líneas de la corrección) y la sección 4 (pesos como imagen).
**Deben ver:** errores por época bajando (~45, ~24…) y **99.8 %** en el examen.
**Pesos como imagen:** rojo en el centro (donde el 1 tiene tinta), azul en el anillo (donde el 0). *¿Qué está mirando la neurona?*
**Errores típicos:** `w = eta * error * xi` (falta sumar el `w` anterior); usar `y` en vez de `yi`.

## Paso 4 · Desafío 3 vs 5 (25 min)
**Haz:** `A, B = 3, 5` y ejecutar todo.
**Deben ver:** ~800, ~650, ~640 errores por época: **nunca se calma**. La precisión queda ~95 % y cambia según las últimas imágenes que vio.
**Pregunta:** *¿por qué?* La regla solo sabe si acertó, no **cuánto** se equivocó: mismo empujón por un error mínimo que por uno enorme.

## Cierre (12 min)
- Neurona = **suma ponderada + decisión**. Aprender = **corregir los pesos cuando se equivoca**. Límite: no mide cuánto se equivocó.
- **Tarea:** terminar `P2`; probar 3 vs 5 con `epocas=10`.
- **Refuerzo opcional:** notebooks `1_01`, `1_02`, `1_03_1`, `1_03_2`.
- **Próxima clase:** *«es un 5 con 80 % de seguridad»* y bajar el error poco a poco.

---

# PARTE C — Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `NameError: name 'neurona' is not defined` | No ejecutaron la celda donde se define | Ejecutar desde arriba (**Run All**) |
| `TypeError: unsupported operand ... 'ellipsis'` | Quedó un `...` sin completar | Buscar los `...` y reemplazarlos |
| La precisión queda en ~50 % después de entrenar | La regla no actualiza (falta `w +`) | `w = w + eta * error * xi` |
| `ValueError: The truth value of an array ... is ambiguous` | Usaron `if` con muchas imágenes | Usar `(x @ w + b > 0).astype(int)` |
| El entrenamiento tarda mucho | Lo están corriendo con las 60 000 imágenes | Revisar que la celda de filtro (`A, B`) se haya ejecutado |
