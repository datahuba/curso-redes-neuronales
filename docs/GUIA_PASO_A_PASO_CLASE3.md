# Guía paso a paso — Clase 3: Aprender bajando la montaña

**Proyecto:** reconocedor de dígitos escritos a mano, en Python y NumPy.
**Pieza de hoy:** una neurona con **sigmoide** que da probabilidades y aprende con **descenso por gradiente**: distingue 3 de 5 con **~96 %**.
**Problema que resolvemos:** el perceptrón solo dice 0/1 y su regla no sabe *cuánto* se equivocó; con 3 vs 5 nunca deja de saltar.
**Duración:** ~2 h 30 min
**Material:** diapositivas `Clase3_Diapositivas` · notebook `proyecto/P3_aprender_con_gradiente.ipynb`
**Lectura opcional:** [descenso por gradiente](https://irvingvasquez.github.io/libro_redes_neuronales/) en el libro del Dr. Irving Vasquez

## Objetivos de la clase

Al terminar, cada alumno podrá:
1. Explicar por qué la **sigmoide** convierte la neurona en algo que da probabilidades.
2. Explicar el descenso por gradiente con la analogía de la montaña y el efecto de la **tasa de aprendizaje**.
3. Entrenar una neurona sigmoide con descenso por gradiente y leer su **curva de aprendizaje**.

## Agenda

| Tiempo | Tema |
|---|---|
| 0:00 | Repaso: el perceptrón con 3 vs 5 no se calma (10 min) |
| 0:10 | La sigmoide, notebook `P3` sección 1 (20 min) |
| 0:30 | La montaña con niebla: pendiente y paso (20 min) |
| 0:50 | Práctica: descenso con un número, sección 2 (20 min) |
| 1:10 | Descanso (10 min) |
| 1:20 | Error medible y pendiente de la neurona (15 min) |
| 1:35 | Práctica: entrenar 3 vs 5, sección 3 (30 min) |
| 2:05 | ¿Cuándo duda? Sección 4 y puesta en común (15 min) |
| 2:20 | Cierre (10 min) |

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

**Docente:** ejecuta `notebooks_resueltos/proyecto/P3_aprender_con_gradiente.ipynb` para tener las gráficas de las tres tasas de aprendizaje y la curva final.

---

# PARTE B — La clase paso a paso

## 1. Repaso y problema (10 min)

Muestra los errores por época del perceptrón con 3 vs 5 (sube, baja, sube…). Pregunta: *¿qué información le falta a la regla de Rosenblatt?* → Saber **cuánto** se equivocó. Un 5 dudoso y un 5 clarísimo mal clasificados reciben el mismo empujón.

Dos arreglos para hoy: **una salida suave** y **un error que se pueda medir y bajar**.

## 2. La sigmoide (20 min)

$$\sigma(z) = \frac{1}{1 + e^{-z}}$$

- Es un escalón «suavizado». Muy negativo → 0, muy positivo → 1, cero → 0.5.
- Ahora la salida se lee como **probabilidad**: 0.8 = «80 % seguro de que es un 5».
- Lo importante: como es suave, si muevo un poquito un peso, la salida cambia un poquito. Eso permite **medir hacia dónde mejorar**.

Ejercicio 1 del notebook: escribirla con `np.exp` y comparar la gráfica con el escalón.

## 3. La montaña con niebla (20 min)

Historia: estás en una montaña con niebla y quieres llegar al fondo del valle (el **error mínimo**). No ves nada, solo sientes la **pendiente** bajo tus pies.

- Si la pendiente es positiva (el suelo sube hacia la derecha), da un paso a la **izquierda**, y al revés.
- Regla: `w ← w − η · pendiente`.
- La **pendiente** es la **derivada**. Basta saber que dice hacia dónde sube la función y qué tan empinada está. Ejemplo: para $E(w) = (w-3)^2$, la pendiente es $2(w-3)$: negativa a la izquierda de 3, positiva a la derecha, cero en el fondo.

## 4. Práctica: descenso con un número (20 min)

Sección 2 del notebook. Las tres gráficas son la clase:

| `eta` | Qué pasa |
|---|---|
| 0.1 | Baja suave hasta 3 |
| 0.5 | Llega en **un solo paso** (casualidad de esta función) |
| 1.05 | **Rebota y se aleja**: diverge |

Que prueben `0.01` (lentísimo) y `0.9` (zigzag pero llega). Conclusión: **la tasa de aprendizaje es la decisión más importante al entrenar**.

## 5. Error medible y pendiente de la neurona (15 min)

- **Error (entropía cruzada):** castiga mucho estar muy seguro y equivocado. Se da hecha; lo importante es que es **un solo número que queremos bajar**.
- La pendiente para la neurona sigmoide con este error resulta muy simple:

$$\text{grad}_w = \frac{1}{n} X^\top (p - y) \qquad \text{grad}_b = \text{promedio}(p - y)$$

- Léanla en voz alta: **(lo que dijo − lo correcto) × entrada**. ¡Es casi la regla de Rosenblatt! La diferencia: `p − y` ya no es solo +1/−1, es **cuánto** se equivocó.
- `X.T @ (p - y)` hace el cálculo para todas las imágenes a la vez y las suma.

*Para alumnos curiosos:* la deducción usa la regla de la cadena; la derivada de la sigmoide se cancela con la del logaritmo. Si alguien pregunta, se ve en la Clase 5 con la retropropagación.

## 6. Práctica: entrenar 3 vs 5 (30 min)

Ejercicio 3. Resultado esperado: la curva de error baja suave (sin saltos) y la precisión llega a **~96 %**. El perceptrón sacaba ~95 %, pero sin calmarse nunca y sin decir qué tan seguro estaba: la mejora de hoy es sobre todo **estabilidad y probabilidades**, que es lo que permitirá apilar capas.

Preguntas para la clase:
- *¿Por qué la curva baja rápido al principio y luego despacio?* Cerca del fondo la pendiente es chica → pasos chicos.
- *¿Qué pasa con `eta=5`?* Que lo prueben.

**Errores típicos:** `grad_w = X @ (p - y)` (falta la `.T`: da error de tamaños); olvidar dividir por `len(X)` (con `eta=0.5` explota).

## 7. ¿Cuándo duda? (15 min)

Sección 4: las imágenes con probabilidad cercana a 50 %. Casi siempre son 3 y 5 que **también harían dudar a una persona**. Eso es una ventaja enorme: la red sabe cuándo no sabe.

## 8. Cierre (10 min)

- **Sigmoide** → probabilidades. **Error medible** + **descenso por gradiente** → aprender bajando el error poco a poco.
- La **curva de aprendizaje** se mira siempre.

**Tarea:** terminar `P3`; probar con otros pares de dígitos (4 vs 9, 1 vs 7). ¿Cuál es el más difícil?
**Refuerzo opcional:** `notebooks/1_04_red_neuronal_simple` y `1_05_descenso_por_gradiente_1D`.
**Próxima clase:** 10 neuronas, una por dígito… y **dibujarán sus propios números**.

---

# PARTE C — Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `ValueError: matmul: ... size 11552 is different from 784` | `X @ (p - y)` sin transponer | `X.T @ (p - y)` |
| El error sale `nan` o crece | `eta` muy grande o falta dividir por `len(X)` | Revisar el promedio; probar `eta=0.5` |
| `RuntimeWarning: overflow in exp` | Pesos enormes por divergencia | Mismo arreglo; reiniciar el kernel |
| La curva es plana | No se actualizan `w, b` (quedó un `...`) | Completar la última línea del ciclo |
