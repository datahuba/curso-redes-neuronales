# Guía paso a paso — Clase 4: Diez neuronas: reconocer del 0 al 9

**Proyecto:** reconocedor de dígitos escritos a mano, en Python y NumPy.
**Pieza de hoy:** 10 neuronas con **softmax** que reconocen los 10 dígitos con **~92 %**. Entrenamiento por **lotes**. Y el primer momento «wow»: **cada alumno dibuja sus números** y su red los lee.
**Problema que resolvemos:** hasta ahora solo respondíamos preguntas de sí/no (0 o 1, 3 o 5).
**Duración:** ~2 h 30 min
**Material:** diapositivas `Clase4_Diapositivas` · notebook `proyecto/P4_diez_neuronas.ipynb` · programa `proyecto/dibujar.py`

## Objetivos de la clase

Al terminar, cada alumno podrá:
1. Representar etiquetas en formato **one-hot** y explicar **softmax**.
2. Entrenar 10 neuronas a la vez con matrices de pesos y **mini-lotes**.
3. Leer una **matriz de confusión** para saber con qué se equivoca la red.
4. Probar su red con dibujos propios.

## Agenda

| Tiempo | Tema |
|---|---|
| 0:00 | Repaso y el problema: 10 respuestas posibles (10 min) |
| 0:10 | One-hot y softmax, notebook `P4` secciones 1–2 (25 min) |
| 0:35 | La tabla de pesos y la misma pendiente de siempre (10 min) |
| 0:45 | Mini-lotes y Ejercicio 3: entrenar (25 min) |
| 1:10 | Descanso (10 min) |
| 1:20 | ¿Qué mira cada neurona? Matriz de confusión (20 min) |
| 1:40 | ¡A dibujar! `dibujar.py` (30 min) |
| 2:10 | Puesta en común: ¿dónde falla? (10 min) y cierre (10 min) |

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

## 1. Repaso y problema (10 min)

Pregunta: *si una neurona responde sí/no, ¿cuántas necesito para reconocer del 0 al 9?* Deja que lo deduzcan: **10**, una por dígito, todas mirando la misma imagen. Gana la más convencida.

## 2. One-hot y softmax (25 min)

**One-hot:** la respuesta correcta en «10 casillas». `3 → [0,0,0,1,0,0,0,0,0,0]`. El truco `np.eye(10)[y]` les va a encantar: la fila 3 de la identidad es justo eso.

**Softmax:** 10 puntajes cualesquiera → 10 probabilidades que suman 1.
- Ejemplo en el pizarrón: puntajes `[2, 1, 0.1]` → `e^2 = 7.4`, `e^1 = 2.7`, `e^0.1 = 1.1` → total 11.2 → `[0.66, 0.24, 0.10]`.
- La exponencial hace todo positivo y **exagera al ganador**.
- Restar el máximo antes no cambia el resultado (se cancela arriba y abajo) y evita números gigantes.

**Error típico:** `E / E.sum()` sin `axis=1, keepdims=True` → divide entre la suma de **toda** la tabla.

## 3. La tabla de pesos (10 min)

- Antes `w` era una columna de 784. Ahora `W` es una tabla de **784 × 10**: una columna por neurona.
- `X @ W + b` calcula las 10 sumas de todas las imágenes de un golpe.
- La pendiente: **la misma fórmula de la Clase 3**, `X.T @ (P − Y) / n`. Destácalo: no hay nada nuevo que aprender, solo más columnas.

## 4. Mini-lotes y entrenamiento (25 min)

Analogía: para corregir el rumbo no hace falta preguntar a los 60 000 alumnos de la ciudad; con una encuesta de 128 ya sabes hacia dónde ir. **Muchos pasos con lotes chicos > pocos pasos con todo.**
- Mezclar (`permutation`) en cada época evita que aprenda en un orden raro.
- Una época ≈ 470 pasos.

Resultado esperado: el error baja de ~0.35 a ~0.27 y la precisión llega a **~92 %**. Recuérdales la tabla del recorrido: 82 % (plantillas) → 92 %.

## 5. ¿Qué mira cada neurona? (20 min)

- **Pesos como imágenes:** se ven «fantasmas» de cada dígito; compáralos con las plantillas de la Clase 1. Diferencia: ahora también hay **azul** (lo que resta).
- **Matriz de confusión:** fila = correcto, columna = lo que dijo. Que encuentren las confusiones más grandes (suelen ser 4↔9, 3↔5, 7↔9, 2↔8). *¿Tiene sentido?*

## 6. ¡A dibujar! (30 min)

1. En el notebook: `guardar_pesos(W1=W, b1=b)`.
2. Abrir una terminal **en la carpeta `proyecto/`** (en VS Code: clic derecho sobre la carpeta → *Open in Integrated Terminal*), con `(nni)` activo:

```bash
python dibujar.py
```

3. Dibujar con clic izquierdo; clic derecho borra. La ventana muestra la predicción y las 10 probabilidades.

**En Colab:** dibujar en Paint (fondo negro o blanco, trazo **grueso**), guardar como `mi_numero.png`, subirlo con el ícono de carpeta y ejecutar la última celda del notebook.

Mini-competencia: *¿quién logra engañar a la red con un número que una persona leería sin problema?* Pídeles que anoten qué lo engaña (número chico, muy inclinado, trazo fino, un 1 con base…).

## 7. Cierre (10 min)

- 10 neuronas + softmax = clasificador de 10 clases. Mini-lotes = entrenar rápido.
- Límite: cada neurona separa con **una línea recta** (modelo lineal). Aunque entrenes más, se queda en ~92 %.

**Tarea:** terminar `P4` y traer anotados 3 dibujos que engañan a la red.
**Refuerzo opcional:** `notebooks/1_06_descenso_unpaso`, `1_07_descenso_por_gradiente` y `1_08_adaline`.
**Próxima clase:** una **capa oculta** → de 92 % a 97 %.

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
