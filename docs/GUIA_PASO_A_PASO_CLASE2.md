# Guía paso a paso — Clase 2: Una neurona que aprende de sus errores

**Proyecto:** reconocedor de dígitos escritos a mano, en Python y NumPy.
**Pieza de hoy:** una neurona (el perceptrón) que distingue el 0 del 1 con **99.8 %** de aciertos y corrige sus pesos cada vez que se equivoca.
**Problema que resolvemos:** las plantillas de la Clase 1 nunca cambian; si se equivocan, no aprenden nada.
**Duración:** ~2 h 30 min
**Material:** diapositivas `Clase2_Diapositivas` · notebook `proyecto/P2_una_neurona.ipynb` · repositorio https://github.com/datahuba/curso-redes-neuronales
**Lectura opcional** (libro del Dr. Irving Vasquez): [Neurona de McCulloch y Pitts y perceptrón](https://irvingvasquez.github.io/libro_redes_neuronales/)

## Objetivos de la clase

Al terminar, cada alumno podrá:
1. Explicar qué hace una neurona artificial: **suma ponderada + decisión**.
2. Programar una neurona y encontrar a mano los pesos de una compuerta AND.
3. Aplicar la **regla de aprendizaje de Rosenblatt** y entrenar una neurona con imágenes reales.
4. Interpretar los pesos aprendidos como una imagen.

## Agenda

| Tiempo | Tema |
|---|---|
| 0:00 | Repaso de la Clase 1 y el problema de hoy (10 min) |
| 0:10 | ¿Qué hace una neurona? De la biológica a `x @ w + b` (15 min) |
| 0:25 | Práctica: compuerta AND a mano, notebook `P2` sección 1 (15 min) |
| 0:40 | Práctica: los datos 0/1 y la neurona, secciones 2 y Ejercicio 1 (20 min) |
| 1:00 | Descanso (10 min) |
| 1:10 | La regla de Rosenblatt, en el pizarrón con un ejemplo (20 min) |
| 1:30 | Práctica: entrenar, Ejercicio 2, y mirar los pesos (25 min) |
| 1:55 | Desafío 3 vs 5 y puesta en común (25 min) |
| 2:20 | Cierre (10 min) |

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

## 1. Repaso y problema (10 min)

Pregunta: *¿cuánto acertaban las plantillas? ¿Qué pasaba cuando se equivocaban?* → 82 %, y **no aprendían nada** del error.

Plantea el problema de hoy: **queremos algo que se corrija solo.** Para empezar, una pregunta fácil: ¿esta imagen es un 0 o un 1?

## 2. ¿Qué hace una neurona? (15 min)

Analogía para decidir si vas a un partido: entradas = ¿hace buen tiempo?, ¿van tus amigos?, ¿tienes plata? Cada una pesa distinto (los amigos importan más → peso grande). Sumas, y si pasa un umbral, vas.

- **Pesos** `w`: cuánto importa cada entrada (pueden ser negativos: «esto me hace decir que no»).
- **Sesgo** `b`: qué tan fácil es decir que sí (el umbral, cambiado de signo).
- **Decisión:** `1` si `x @ w + b > 0`, `0` si no.

Contexto histórico en 1 minuto: McCulloch y Pitts (1943) propusieron la neurona con pesos fijos; Rosenblatt (1958) le agregó **aprender los pesos**. Eso es lo que haremos.

Explica `@` (producto punto): multiplica casilla por casilla y suma. Con una imagen son 784 multiplicaciones en una línea.

## 3. Práctica: compuerta AND (15 min)

Notebook `P2`, sección 1. Que lo intenten **sin pistas** 5 minutos. Una solución: pesos `1, 1` y sesgo entre −2 y −1 (por ejemplo −1.5).

Pregunta a la clase: *¿y la compuerta OR?* (mismo peso, sesgo −0.5). *¿Hay una sola respuesta correcta?* No: infinitas. Por eso se puede **aprender**.

Remata: con 784 entradas nadie busca pesos a mano.

## 4. Práctica: los datos y la neurona (20 min)

Sección 2 y Ejercicio 1.
- `y` vale 1 si la imagen es el dígito `B` (1) y 0 si es `A` (0).
- La neurona con `(x @ w + b > 0).astype(int)` sirve **para una imagen o para muchas** a la vez (si `x` tiene muchas filas). Esa es la magia de NumPy.
- Con pesos al azar: ~50 %. Como tirar una moneda.

**Error típico:** escribir `if x @ w + b > 0: return 1` → funciona con una imagen pero falla con muchas. Que usen la versión con `.astype(int)`.

## 5. La regla de Rosenblatt (20 min)

En el pizarrón, con una «imagen» de 3 píxeles `x = [1, 0, 1]`, pesos `w = [0, 0, 0]`, `b = 0`, `η = 0.1`, respuesta correcta `y = 1`:

1. Suma: `0` → la neurona dice `0`. Error = `y − ŷ = 1 − 0 = +1`.
2. `w ← w + η · error · x = [0.1, 0, 0.1]`, `b ← 0.1`.
3. Siguiente vez: suma = `0.1 + 0.1 + 0.1 = 0.3 > 0` → dice `1`. ✅

Intuición: **solo cambian los pesos de los píxeles encendidos**, en la dirección que habría evitado el error. Si acierta, error = 0 y no cambia nada.

## 6. Práctica: entrenar y mirar los pesos (25 min)

Ejercicio 2 y sección 4.
- Se equivoca ~45 veces en la primera época y cada vez menos. **Esto es aprender.**
- Precisión en el examen: ~99.8 %.
- La imagen de los pesos: rojo en el centro (donde el 1 tiene tinta) y azul en el anillo (donde el 0 tiene tinta). Pregunta: *¿qué está mirando la neurona?*

**Errores típicos:** escribir `w = eta * error * xi` (falta sumar el `w` anterior); usar `y` en lugar de `yi`.

## 7. Desafío 3 vs 5 (25 min)

Que cambien `A, B = 3, 5` y vuelvan a ejecutar todo. Observaciones esperadas:
- Los errores por época **no bajan a cero**: se quedan en ~600 por época (con 0 vs 1 eran ~25).
- La precisión en el examen baja a ~95 % y depende de cuáles fueron las últimas imágenes que vio.

Pregunta: *¿por qué?* Porque 3 y 5 se parecen mucho y la regla solo sabe si acertó o no, **no cuánto** se equivocó: da el mismo empujón por un error mínimo que por uno enorme. Además, no siempre existe una sola «línea» que los separe a todos.

## 8. Cierre (10 min)

- Una neurona = **suma ponderada + decisión**. Los pesos dicen qué le importa.
- Aprender = **corregir los pesos cuando se equivoca**.
- Límite: solo dice 0/1 y no mide cuánto se equivocó.

**Tarea:** terminar `P2` y probar `epocas=10` con 3 vs 5. ¿Llega a cero errores?
**Refuerzo opcional:** notebooks `notebooks/1_01_mcculloch_pitts`, `1_02_perceptron_AND`, `1_03_1_perceptron_simple` y `1_03_2_regla_de_aprendizaje`.
**Próxima clase:** una neurona que dice *«es un 5 con 80 % de seguridad»* y aprende bajando su error poco a poco.

---

# PARTE C — Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `NameError: name 'neurona' is not defined` | No ejecutaron la celda donde se define | Ejecutar desde arriba (**Run All**) |
| `TypeError: unsupported operand ... 'ellipsis'` | Quedó un `...` sin completar | Buscar los `...` y reemplazarlos |
| La precisión queda en ~50 % después de entrenar | La regla no actualiza (falta `w +`) | `w = w + eta * error * xi` |
| `ValueError: The truth value of an array ... is ambiguous` | Usaron `if` con muchas imágenes | Usar `(x @ w + b > 0).astype(int)` |
| El entrenamiento tarda mucho | Lo están corriendo con las 60 000 imágenes | Revisar que la celda de filtro (`A, B`) se haya ejecutado |
