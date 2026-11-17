# Guía paso a paso — Clase 4: Diez neuronas: reconocer del 0 al 9

**Proyecto:** reconocedor de dígitos escritos a mano, en Python y NumPy.
**Pieza de hoy:** 10 neuronas con **softmax** que reconocen los 10 dígitos con **~92 %**. Entrenamiento por **lotes**. Y el primer momento «wow»: **cada alumno dibuja sus números** y su red los lee.
**Problema que resolvemos:** hasta ahora solo respondíamos preguntas de sí/no (0 o 1, 3 o 5).
**Duración:** ~2 h de clase, más 15–30 min de margen para dudas
**Material:** diapositivas `Clase4_Diapositivas` · notebook `proyecto/P4_diez_neuronas.ipynb` · programa `proyecto/dibujar.py`

## Objetivos de la clase

Al terminar, cada alumno podrá:
1. Representar etiquetas en formato **one-hot** y explicar **softmax**.
2. Entrenar 10 neuronas a la vez con matrices de pesos y **mini-lotes**.
3. Leer una **matriz de confusión** para saber con qué se equivoca la red.
4. Probar su red con dibujos propios.

## Agenda

> **Cómo se da esta clase:** directo a la práctica. Los alumnos abren el notebook en el minuto 2 y la teoría entra en **pausas cortas** (⏸) justo cuando el ejercicio la necesita. Regla de oro: **primero lo hacen, después lo explicas** (o, si hace falta para poder hacerlo, lo explicas en 3–5 minutos y vuelven al teclado). Las diapositivas siguen el mismo orden: «Paso» (oscuras) = trabajan; «Pausa · teoría» (claras) = explicas.

| Tiempo | Qué pasa |
|---|---|
| 0:00 | Abrir `P4` y la misión de hoy (3 min) |
| 0:03 | **Paso 1** · One-hot y softmax (20 min) |
| 0:23 | ⏸ Pausa: lo que acabas de programar (4 min) |
| 0:27 | ⏸ Pausa: la tabla de pesos y los mini-lotes (4 min) |
| 0:31 | **Paso 2** · Entrenar por mini-lotes (25 min) |
| 0:56 | Descanso (10 min) |
| 1:06 | **Paso 3** · ¿Qué mira cada neurona? Matriz de confusión (15 min) |
| 1:21 | **Paso 4** · ¡A dibujar! (30 min) |
| 1:51 | Puesta en común: ¿qué dibujos la engañan?, mapa y cierre (15 min) |

---

# PARTE A — Antes de clase (15 min)

```bash
cd ~\projects\curso-redes-neuronales
```
```bash
git pull
```
```bash
conda activate nni
```

**Docente:**
1. Ejecuta `notebooks_resueltos/proyecto/P4_diez_neuronas.ipynb`.
2. En una terminal, dentro de `notebooks_resueltos/proyecto/`, prueba `python dibujar.py`. Debe abrir una ventana negra donde se dibuja con el mouse.

**Verifica en las computadoras de los alumnos** que `python -c "import tkinter"` no da error (viene con Anaconda). Quien use Colab dibujará en Paint (ver sección 6).

---

# PARTE B — La clase paso a paso

## Arranque (3 min)
Pregunta mientras abren `proyecto/P4_diez_neuronas.ipynb`: *si una neurona responde sí o no, ¿cuántas necesito para reconocer del 0 al 9?* → **10**, una por dígito; gana la más convencida. Y hoy terminan **dibujando**.

## Paso 1 · One-hot y softmax (20 min)
**Haz:** Ejercicio 1 (`np.eye(10)[y]`) y Ejercicio 2 (softmax; la fórmula está en el notebook).
**Deben ver:** `✅ one_hot(3) tiene un 1 en la casilla 3` y `✅ cada fila suma 1`.
**Error típico:** `E / E.sum()` sin `axis=1, keepdims=True` → divide entre la suma de toda la tabla.

## ⏸ Pausa: lo que acabas de programar (4 min)
- **One-hot:** la respuesta correcta en 10 casillas.
- **Softmax** en el pizarrón: `[2, 1, 0.1]` → `e²=7.4, e¹=2.7, e^0.1=1.1` → total 11.2 → `[0.66, 0.24, 0.10]`. La exponencial hace todo positivo y **exagera al ganador**. Restar el máximo no cambia nada (se cancela arriba y abajo) y evita números gigantes.

## ⏸ Pausa: la tabla de pesos y los mini-lotes (4 min)
- `W` es una tabla de **784 × 10**, una columna por neurona; `X @ W + b` da 10 puntajes por imagen.
- La pendiente es **la misma de la Clase 3**: `Xᵀ(P − Y) / n`. Nada nuevo, solo más columnas.
- **Mini-lotes:** para corregir el rumbo no hace falta preguntar a 60 000; con una encuesta de 128 ya sabes hacia dónde ir. Muchos pasos chicos > pocos pasos con todo.

## Paso 2 · Entrenar por mini-lotes (25 min)
**Haz:** Ejercicio 3 (el paso dentro del ciclo).
**Deben ver:** error de ~0.35 a ~0.27 y **~92 %**. Señala el mapa: 82 % → 92 %.

## Descanso (10 min)

## Paso 3 · ¿Qué mira cada neurona? (15 min)
**Haz:** secciones 5 y 6.
- **Pesos como imágenes:** «fantasmas» de cada dígito; compáralos con las plantillas de la Clase 1. Ahora también hay **azul** (lo que resta).
- **Matriz de confusión:** fila = correcto, columna = lo que dijo. Que encuentren las confusiones más grandes (4↔9, 3↔5, 7↔9). *¿Tiene sentido?*

## Paso 4 · ¡A dibujar! (30 min)
1. En el notebook: `guardar_pesos(W1=W, b1=b)`.
2. Terminal **en la carpeta `proyecto/`** (VS Code: clic derecho sobre la carpeta → *Open in Integrated Terminal*), con `(nni)` activo:

```bash
python dibujar.py
```

3. Clic izquierdo dibuja, clic derecho borra.

**Colab:** dibujar en Paint (trazo grueso), guardar `mi_numero.png`, subirlo y ejecutar la última celda.
**Mini-competencia:** *¿quién engaña a la red con un número que una persona leería sin problema?* Que anoten qué la engaña.

## Cierre (15 min)
- Puesta en común de los dibujos que engañan (número chico, inclinado, trazo fino…).
- Límite: cada neurona separa con **una línea recta**; entrenar más no ayuda, se queda en ~92 %.
- **Tarea:** terminar `P4` y traer 3 dibujos que engañan a la red.
- **Refuerzo opcional:** `1_06`, `1_07`, `1_08`.
- **Próxima clase:** capa oculta → de 92 % a 97 %.

---

# PARTE C — Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `No encuentro pesos.npz` al abrir `dibujar.py` | No ejecutaron `guardar_pesos` o la terminal no está en `proyecto/` | Ejecutar la celda; `cd proyecto` |
| `ModuleNotFoundError: No module named 'digitos'` en la terminal | Terminal fuera de `proyecto/` | `cd ~\projects\curso-redes-neuronales\proyecto` |
| `ModuleNotFoundError: tkinter` | Python sin Tk (raro con Anaconda) | Usar la opción Paint + `leer_dibujo` |
| La ventana no reacciona en Mac | Permisos de Tk | Usar la opción Paint |
| La red falla con todos mis dibujos | Trazo muy fino | Trazo grueso, número grande y centrado |
| Las filas de softmax no suman 1 | Falta `axis=1, keepdims=True` | Ver sección 2 |
