# Guía paso a paso — Clase 3: Aprender bajando la montaña

**Proyecto:** reconocedor de dígitos escritos a mano, en Python y NumPy.
**Pieza de hoy:** una neurona con **sigmoide** que da probabilidades y aprende con **descenso por gradiente**: distingue 3 de 5 con **~96 %**.
**Problema que resolvemos:** el perceptrón solo dice 0/1 y su regla no sabe *cuánto* se equivocó; con 3 vs 5 nunca deja de saltar.
**Duración:** ~2 h de clase, más 15–30 min de margen para dudas
**Material:** diapositivas `Clase3_Diapositivas` · notebook `proyecto/P3_aprender_con_gradiente.ipynb`
**Lectura opcional:** [descenso por gradiente](https://irvingvasquez.github.io/libro_redes_neuronales/) en el libro del Dr. Irving Vasquez

## Objetivos de la clase

Al terminar, cada alumno podrá:
1. Explicar por qué la **sigmoide** convierte la neurona en algo que da probabilidades.
2. Explicar el descenso por gradiente con la analogía de la montaña y el efecto de la **tasa de aprendizaje**.
3. Entrenar una neurona sigmoide con descenso por gradiente y leer su **curva de aprendizaje**.

## Agenda

> **Cómo se da esta clase:** directo a la práctica. Los alumnos abren el notebook en el minuto 2 y la teoría entra en **pausas cortas** (⏸) justo cuando el ejercicio la necesita. Regla de oro: **primero lo hacen, después lo explicas** (o, si hace falta para poder hacerlo, lo explicas en 3–5 minutos y vuelven al teclado). Las diapositivas siguen el mismo orden: «Paso» (oscuras) = trabajan; «Pausa · teoría» (claras) = explicas.

| Tiempo | Qué pasa |
|---|---|
| 0:00 | Abrir `P3` y la misión de hoy (3 min) |
| 0:03 | **Paso 1** · La sigmoide (10 min) |
| 0:13 | ⏸ Pausa: de «sí/no» a «qué tan seguro» (3 min) |
| 0:16 | ⏸ Pausa: la montaña con niebla (5 min) |
| 0:21 | **Paso 2** · Bajar la montaña con un número (20 min) |
| 0:41 | Puesta en común: la tasa de aprendizaje (5 min) |
| 0:46 | Descanso (10 min) |
| 0:56 | ⏸ Pausa: la pendiente de la neurona (5 min) |
| 1:01 | **Paso 3** · Entrenar 3 vs 5 (30 min) |
| 1:31 | **Paso 4** · ¿Cuándo duda? (15 min) |
| 1:46 | Mapa y cierre (10 min) |

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

## Arranque (3 min)
Mientras abren `proyecto/P3_aprender_con_gradiente.ipynb`: *el perceptrón con 3 vs 5 nunca se calmaba porque no sabe cuánto se equivocó. Hoy: una neurona que dice «80 % seguro» y aprende bajando su error.*

## Paso 1 · La sigmoide (10 min)
**Haz:** Ejercicio 1 (la fórmula está en el notebook) y mirar la gráfica comparada con el escalón.
**Deben ver:** `✅ la sigmoide va de 0 a 1`.

## ⏸ Pausa: de «sí/no» a «qué tan seguro» (3 min)
Sobre la gráfica que ya tienen: es un escalón suavizado. Muy negativo → 0, muy positivo → 1, cero → 0.5. Se lee como **probabilidad**. Y lo clave: como es suave, si muevo un poquito un peso, la salida cambia un poquito → **se puede medir hacia dónde mejorar**.

## ⏸ Pausa: la montaña con niebla (5 min)
Estás en una montaña con niebla y quieres el fondo del valle (el **error mínimo**). Solo sientes la **pendiente** bajo los pies: da un paso cuesta abajo, vuelve a sentir, repite.
- Regla: `w ← w − η · pendiente`. La pendiente es la **derivada**: dice hacia dónde sube y qué tan empinado.
- Ejemplo en el pizarrón: $E(w) = (w-3)^2$, pendiente $2(w-3)$: negativa a la izquierda de 3, positiva a la derecha, cero en el fondo.

## Paso 2 · Bajar la montaña con un número (20 min)
**Haz:** Ejercicio 2 (una línea) y probar `eta` = 0.01, 0.1, 0.5, 0.9, 1.05.
**Deben ver:** con 0.1 baja suave hasta 3; con 0.5 llega de un salto; con 1.05 **rebota y se aleja**.

## Puesta en común (5 min)
Que cuenten qué vio cada uno. Conclusión: **la tasa de aprendizaje es la decisión más importante al entrenar.**

## Descanso (10 min)

## ⏸ Pausa: la pendiente de la neurona (5 min)
- **Error (entropía cruzada):** castiga estar muy seguro y equivocado. Viene hecho; es *un número que queremos bajar*.
- La pendiente: `grad_w = Xᵀ(p − y) / n`. Léanla en voz alta: **(lo que dijo − lo correcto) × entrada**. ¡Casi Rosenblatt! Pero `p − y` dice **cuánto** se equivocó.
- *Para curiosos:* la derivada de la sigmoide se cancela con la del logaritmo; lo veremos con la retropropagación.

## Paso 3 · Entrenar 3 vs 5 (30 min)
**Haz:** Ejercicio 3: predecir, calcular pendientes, dar el paso.
**Deben ver:** la curva de error bajando **suave, sin saltos**, y **~96 %** de precisión. (El perceptrón sacaba ~95 %, pero sin calmarse nunca y sin decir qué tan seguro estaba.)
**Preguntas:** *¿por qué baja rápido al principio y lento al final?* (cerca del fondo la pendiente es chica). *¿Qué pasa con `eta=5`?*
**Errores típicos:** `X @ (p - y)` sin `.T` (error de tamaños); no dividir por `len(X)` (explota).

## Paso 4 · ¿Cuándo duda? (15 min)
**Haz:** sección 4: las imágenes con probabilidad cerca de 50 %.
**Comenten:** casi siempre son 3 y 5 que **también harían dudar a una persona**. La red sabe cuándo no sabe.

## Cierre (10 min)
- Sigmoide → probabilidades. Error medible + descenso por gradiente → aprender poco a poco. La curva de aprendizaje se mira siempre.
- **Tarea:** terminar `P3`; probar 4 vs 9 y 1 vs 7. ¿Cuál es el más difícil?
- **Refuerzo opcional:** `1_04`, `1_05`.
- **Próxima clase:** 10 neuronas… y van a dibujar sus números.

---

# PARTE C — Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `ValueError: matmul: ... size 11552 is different from 784` | `X @ (p - y)` sin transponer | `X.T @ (p - y)` |
| El error sale `nan` o crece | `eta` muy grande o falta dividir por `len(X)` | Revisar el promedio; probar `eta=0.5` |
| `RuntimeWarning: overflow in exp` | Pesos enormes por divergencia | Mismo arreglo; reiniciar el kernel |
| La curva es plana | No se actualizan `w, b` (quedó un `...`) | Completar la última línea del ciclo |
