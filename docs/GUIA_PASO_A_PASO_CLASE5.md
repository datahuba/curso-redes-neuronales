# Guía paso a paso — Clase 5: La red de verdad: capa oculta y retropropagación

**Proyecto:** reconocedor de dígitos escritos a mano, en Python y NumPy.
**Pieza de hoy:** una **capa oculta** de 128 neuronas con ReLU, entrenada con **retropropagación**: de 92 % a **~97 %**. Y la comparan dibujando.
**Problema que resolvemos:** el modelo lineal de la Clase 4 se estanca en 92 %; cada neurona solo separa con una línea recta.
**Duración:** ~2 h de clase, más 15–30 min de margen para dudas
**Material:** diapositivas `Clase5_Diapositivas` · notebook `proyecto/P5_red_multicapa.ipynb` · `proyecto/dibujar.py`
**Lectura opcional:** [redes multicapa y retropropagación](https://irvingvasquez.github.io/libro_redes_neuronales/) en el libro del Dr. Irving Vasquez

## Objetivos de la clase

Al terminar, cada alumno podrá:
1. Explicar por qué una **capa oculta** con activación no lineal supera al modelo lineal.
2. Programar el **pase hacia adelante** de una red de dos capas, cuidando los tamaños.
3. Programar la **retropropagación** como «repartir el error hacia atrás» y **verificarla numéricamente**.
4. Entrenar la red y compararla dibujando.

## Agenda

> **Cómo se da esta clase:** directo a la práctica. Los alumnos abren el notebook en el minuto 2 y la teoría entra en **pausas cortas** (⏸) justo cuando el ejercicio la necesita. Regla de oro: **primero lo hacen, después lo explicas** (o, si hace falta para poder hacerlo, lo explicas en 3–5 minutos y vuelven al teclado). Las diapositivas siguen el mismo orden: «Paso» (oscuras) = trabajan; «Pausa · teoría» (claras) = explicas.

| Tiempo | Qué pasa |
|---|---|
| 0:00 | Abrir `P5`: un dibujo que engañó a la red y la misión (5 min) |
| 0:05 | **Paso 1** · ReLU y la red de dos capas (25 min) |
| 0:30 | ⏸ Pausa: lo que armaste, inspectores de rasgos (5 min) |
| 0:35 | Descanso (10 min) |
| 0:45 | ⏸ Pausa: retropropagación, la culpa hacia atrás (10 min) |
| 0:55 | **Paso 2** · Retropropagación y verificación (30 min) |
| 1:25 | **Paso 3** · Entrenar y dibujar (25 min) |
| 1:50 | Resultado (97 %), experimentos si sobra tiempo, mapa y cierre (15 min) |

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

## Arranque (5 min)
Que un alumno muestre un dibujo que engañó a la red de la Clase 4. *Entrenar más no ayuda: se queda en 92 %. Hoy: una capa en medio que aprende rasgos.* Abren `proyecto/P5_red_multicapa.ipynb`.

## Paso 1 · ReLU y la red de dos capas (25 min)
**Haz:** Ejercicio 1 (`relu`), mirar los tamaños de `W1, b1, W2, b2`, Ejercicio 2 (`adelante`: tres líneas).
**Deben ver:** `W1 (784, 128)` … y probabilidades ~0.1 (sin entrenar, la red no sabe nada); `✅ adelante() da 10 probabilidades por imagen`.
**Si se traban con los tamaños:** en el pizarrón `(n×784)·(784×128) → (n×128)·(128×10) → (n×10)`: **los números de adentro deben coincidir**.

## ⏸ Pausa: lo que armaste (5 min)
Analogía de la fábrica: en vez de que el jefe (salida) mire 784 píxeles, contrata **128 inspectores** (capa oculta); cada uno aprende a detectar un **rasgo** (un círculo arriba, una raya…) y el jefe decide con sus informes. Nadie les dice qué buscar: lo aprenden.
- *Pregunta trampa:* ¿y sin ReLU? Dos multiplicaciones de matrices seguidas = una sola → otra vez lineal.
- Pesos al azar: si todos empiezan en 0, los 128 inspectores aprenderían lo mismo.

## Descanso (10 min)

## ⏸ Pausa: retropropagación (10 min)
**El corazón del curso.** Primero sin fórmulas: *el error se mide en la salida; para corregir a un inspector hay que saber cuánta culpa tuvo. Más culpa si su informe pesaba mucho (`W2` grande) y ninguna si estaba apagado (ReLU en 0).*

Luego los 5 pasos (dibuja la red y márcala hacia atrás):

| Paso | Código | En palabras |
|---|---|---|
| 1 | `dZ2 = (P - Y) / n` | error de la salida (como en la Clase 4) |
| 2 | `dW2 = A1.T @ dZ2` | pendiente capa 2: error × entrada |
| 3 | `dA1 = dZ2 @ W2.T` | culpa de cada neurona oculta |
| 4 | `dZ1 = dA1 * (Z1 > 0)` | si estaba apagada, culpa 0 |
| 5 | `dW1 = X.T @ dZ1` | pendiente capa 1: ¡la misma receta! |

No hay matemática nueva: es la **regla de la cadena**, capa por capa. Y directo al teclado.

## Paso 2 · Retropropagación y verificación (30 min)
**Haz:** Ejercicio 3 (una línea por paso) y ejecutar la verificación numérica.
**Deben ver:** «tu función» y «a mano» iguales, `✅` en W1 y W2. Cuéntales que **así depuran redes los profesionales**.
**Errores típicos:** `A1 @ dZ2` sin `.T`; `dZ2 @ W2` sin `.T`; `dZ1 = dA1 * Z1` (debe ser la máscara `Z1 > 0`). ❌ en W1 pero ✅ en W2 → el error está en los pasos 3–5.

## Paso 3 · Entrenar y dibujar (25 min)
**Haz:** sección 5 (el mismo ciclo de la Clase 4) y sección 6: `guardar_pesos(**red)` y `python dibujar.py`.
**Deben ver:** 94 % → 97 % en 5 épocas (~40 s). Que prueben **los dibujos que engañaban** a la red de la Clase 4.

## Resultado y cierre (15 min)
- **97 %**: de 8 errores cada 100 a 3.
- Si sobra tiempo, experimentos de la sección 7 (16 vs 512 neuronas ocultas, otro `eta`, sigmoide en vez de ReLU).
- **Tarea:** terminar `P5` + un experimento; anotar precisión y tiempo.
- **Refuerzo opcional:** `1_09`, `1_10`, `1_11` (XOR).
- **Próxima clase:** entrenar más rápido: optimizadores.

---

# PARTE C — Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `ValueError: matmul ... mismatch` | Falta un `.T` | Revisar tamaños con `print(A.shape)` en cada paso |
| ❌ en la verificación de `W1` pero ✅ en `W2` | Error en los pasos 3–5 | Revisar la máscara `(Z1 > 0)` y `dZ2 @ W2.T` |
| ❌ en ambas | Falta dividir por `n` en `dZ2` o `dW2` mal | Revisar paso 1 y 2 |
| La precisión queda en ~10 % | Divergió (`eta` grande) o pesos iniciales en cero | Volver a `crear_red()` y `eta=0.1` |
| El entrenamiento tarda varios minutos | Computadora lenta | `epocas=2` alcanza para ~95 % |
