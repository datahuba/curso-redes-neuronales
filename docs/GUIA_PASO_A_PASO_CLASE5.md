# Guía paso a paso — Clase 5: La red de verdad: capa oculta y retropropagación

**Proyecto:** reconocedor de dígitos escritos a mano, en Python y NumPy.
**Pieza de hoy:** una **capa oculta** de 128 neuronas con ReLU, entrenada con **retropropagación**: de 92 % a **~97 %**. Y la comparan dibujando.
**Problema que resolvemos:** el modelo lineal de la Clase 4 se estanca en 92 %; cada neurona solo separa con una línea recta.
**Duración:** ~2 h 30 min
**Material:** diapositivas `Clase5_Diapositivas` · notebook `proyecto/P5_red_multicapa.ipynb` · `proyecto/dibujar.py`
**Lectura opcional:** [redes multicapa y retropropagación](https://irvingvasquez.github.io/libro_redes_neuronales/) en el libro del Dr. Irving Vasquez

## Objetivos de la clase

Al terminar, cada alumno podrá:
1. Explicar por qué una **capa oculta** con activación no lineal supera al modelo lineal.
2. Programar el **pase hacia adelante** de una red de dos capas, cuidando los tamaños.
3. Programar la **retropropagación** como «repartir el error hacia atrás» y **verificarla numéricamente**.
4. Entrenar la red y compararla dibujando.

## Agenda

| Tiempo | Tema |
|---|---|
| 0:00 | Repaso: ¿qué dibujos engañaron a la red? El techo del 92 % (10 min) |
| 0:10 | La idea de la capa oculta: rasgos (15 min) |
| 0:25 | ReLU y pase hacia adelante, notebook `P5` secciones 1–3 (25 min) |
| 0:50 | Descanso (10 min) |
| 1:00 | Retropropagación en el pizarrón (25 min) |
| 1:25 | Práctica: Ejercicio 3 y verificación numérica (25 min) |
| 1:50 | Entrenar y dibujar (25 min) |
| 2:15 | Experimentos y cierre (15 min) |

---

# PARTE A — Antes de clase (10 min)

```bash
cd ~\projects\curso-redes-neuronales
```
```bash
git pull
```
```bash
conda activate nni
```

**Docente:** ejecuta `notebooks_resueltos/proyecto/P5_red_multicapa.ipynb` (~1 min de entrenamiento) y deja `dibujar.py` abierto para comparar con la red de la Clase 4.

---

# PARTE B — La clase paso a paso

## 1. Repaso y problema (10 min)

Que muestren los dibujos que engañaron a la red de la Clase 4. Pregunta: *si entreno más épocas, ¿mejora?* → No: se queda en ~92 %. **El modelo es demasiado simple**: cada neurona solo puede trazar una línea recta en el espacio de las imágenes.

## 2. La idea de la capa oculta (15 min)

Analogía de una fábrica: en lugar de que el jefe (salida) mire los 784 píxeles, contrata **128 inspectores** (capa oculta). Cada uno aprende a detectar **un rasgo**: un círculo arriba, una raya vertical, una curva abierta a la derecha… El jefe decide **con esos informes**.

```
imagen (784) → capa oculta (128, ReLU) → salida (10, softmax)
```

- Nadie les dice a los inspectores qué buscar: **lo aprenden** solos.
- Clásico: el XOR no se puede separar con una recta y con una capa oculta sí (si quieres mostrarlo, `notebooks/1_09`–`1_11` lo resuelven).

## 3. ReLU y pase hacia adelante (25 min)

- **ReLU** = `max(0, z)`: deja pasar lo positivo, apaga lo negativo. Pregunta trampa: *¿y si no ponemos activación?* → Dos multiplicaciones de matrices seguidas equivalen a **una sola**: volvemos al modelo lineal.
- **Tamaños**, en el pizarrón: `X (n×784) @ W1 (784×128) → (n×128) @ W2 (128×10) → (n×10)`. La regla: **las dimensiones de adentro deben coincidir**.
- **Pesos al azar**: si todos empiezan en 0, los 128 inspectores aprenderían exactamente lo mismo. El `sqrt(2/784)` es una escala que funciona bien con ReLU («inicialización de He»): no hace falta memorizarlo.

Ejercicios 1 y 2. Sin entrenar, todas las probabilidades salen ~0.1: la red no sabe nada.

## 4. Retropropagación en el pizarrón (25 min)

**Este es el corazón del curso.** Idea, sin fórmulas primero:

> El error se mide en la salida. Para corregir a un inspector, hay que saber **cuánta culpa tuvo** en ese error. Su culpa es mayor si su informe pesaba mucho (`W2` grande) para la neurona que se equivocó. Y si estaba apagado (ReLU en 0), no tuvo culpa.

Luego los 5 pasos (dibuja la red y ve marcando hacia atrás):

| Paso | Código | En palabras |
|---|---|---|
| 1 | `dZ2 = (P - Y) / n` | Error de la salida (como en la Clase 4) |
| 2 | `dW2 = A1.T @ dZ2` | Pendiente de la capa 2: error × entrada (la entrada son los informes `A1`) |
| 3 | `dA1 = dZ2 @ W2.T` | Culpa de cada inspector: el error viaja hacia atrás por los mismos pesos |
| 4 | `dZ1 = dA1 * (Z1 > 0)` | Si estaba apagado, culpa 0 |
| 5 | `dW1 = X.T @ dZ1` | Pendiente de la capa 1: **la misma receta** |

Remata: no hay matemática nueva, es la **regla de la cadena** aplicada capa por capa. Por eso se puede apilar cuantas capas quieras.

## 5. Práctica: retropropagación y verificación (25 min)

Ejercicio 3. La celda de verificación mueve **un** peso un poquito (`1e-5`) y mide cuánto cambia el error: es la definición de pendiente. Si coincide con lo que calculó su función → ✅.

Cuéntales que **así depuran redes los profesionales** cuando programan una capa nueva.

**Errores típicos:** `A1 @ dZ2` en vez de `A1.T @ dZ2` (error de tamaños); `dZ2 @ W2` sin `.T`; `dZ1 = dA1 * Z1` (debe ser la **máscara** `Z1 > 0`).

## 6. Entrenar y dibujar (25 min)

- El ciclo de entrenamiento es **el mismo de la Clase 4**; solo cambió de dónde salen las pendientes. 5 épocas ≈ 40 s: 94 % → 97 %.
- `guardar_pesos(**red)` y `python dibujar.py`. Que prueben **los mismos dibujos que engañaban** a la red de la Clase 4. ¿Cuántos acierta ahora?

## 7. Experimentos y cierre (15 min)

Cada grupo elige uno de la sección 7 y cuenta el resultado:
- `ocultas=16` vs `ocultas=512`: ¿cuánto cambia la precisión y cuánto el tiempo?
- `eta=1.0` (puede diverger) o `eta=0.001` (lentísimo).
- Sigmoide en vez de ReLU (aprende más lento).

**Lo que nos llevamos:** capa oculta = rasgos aprendidos; retropropagación = repartir el error hacia atrás con la misma receta; verificar pendientes numéricamente.

**Tarea:** terminar `P5` y hacer un experimento más. Anotar precisión y tiempo.
**Refuerzo opcional:** `notebooks/1_09_red_multicapa_ejercicio`, `1_10_retropropagacion_base`, `1_11_retropropagacion_completo` (XOR).
**Próxima clase:** entrenar más rápido: optimizadores.

---

# PARTE C — Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `ValueError: matmul ... mismatch` | Falta un `.T` | Revisar tamaños con `print(A.shape)` en cada paso |
| ❌ en la verificación de `W1` pero ✅ en `W2` | Error en los pasos 3–5 | Revisar la máscara `(Z1 > 0)` y `dZ2 @ W2.T` |
| ❌ en ambas | Falta dividir por `n` en `dZ2` o `dW2` mal | Revisar paso 1 y 2 |
| La precisión queda en ~10 % | Divergió (`eta` grande) o pesos iniciales en cero | Volver a `crear_red()` y `eta=0.1` |
| El entrenamiento tarda varios minutos | Computadora lenta | `epocas=2` alcanza para ~95 % |
