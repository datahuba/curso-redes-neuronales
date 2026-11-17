# Guía paso a paso — Clase 6: Entrenar más rápido y mejor (optimizadores)

**Proyecto:** reconocedor de dígitos escritos a mano, en Python y NumPy.
**Pieza de hoy:** **momentum** y **decaimiento de la tasa de aprendizaje**, comparados en una **carrera** con la misma red. La red definitiva llega a **~97.6 %**.
**Problema que resolvemos:** con descenso por gradiente simple, si `eta` es chico tarda una eternidad y si es grande rebota.
**Duración:** ~2 h 15 min
**Material:** diapositivas `Clase6_Diapositivas` · notebook `proyecto/P6_entrenar_mejor.ipynb`

## Objetivos de la clase

Al terminar, cada alumno podrá:
1. Explicar qué es un **optimizador** y por qué es independiente de la red.
2. Programar **momentum** y **decaimiento de la tasa** y explicarlos con analogías.
3. Comparar optimizadores con sus curvas de aprendizaje y elegir uno con argumentos.

## Agenda

| Tiempo | Tema |
|---|---|
| 0:00 | Repaso y problema: el zigzag y la lentitud (10 min) |
| 0:10 | Paso 0: traer las funciones de la Clase 5 (10 min) |
| 0:20 | La pista de carreras y SGD (10 min) |
| 0:30 | Momentum: la pelota que rueda, Ejercicio 1 (25 min) |
| 0:55 | Descanso (10 min) |
| 1:05 | Decaimiento de la tasa, Ejercicio 2 (15 min) |
| 1:20 | ¡La carrera! y experimentos (30 min) |
| 1:50 | La red definitiva + dibujar (15 min) |
| 2:05 | Cierre: Adam y lo que viene (10 min) |

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

**Docente:** ejecuta `notebooks_resueltos/proyecto/P6_entrenar_mejor.ipynb` (~2 min) para tener la gráfica de la carrera.

**Importante:** los alumnos necesitan **su `P5` funcionando** (pegan sus funciones en el Paso 0). Quien no lo terminó, que lo complete al principio con ayuda de un compañero.

---

# PARTE B — La clase paso a paso

## 1. Repaso y problema (10 min)

Recuerda las gráficas de la Clase 3: con `eta` chico, pasos de hormiga; con `eta` grande, rebota. Dibuja un valle **alargado** (como una canaleta): la pendiente apunta casi siempre hacia las paredes, no hacia el fondo → **zigzag**. Así son los errores de las redes reales.

## 2. Paso 0 (10 min)

Pegar `relu`, `softmax`, `crear_red`, `adelante` y `gradientes` del `P5`. Mensaje: **la red no cambia hoy, solo cambia cómo bajamos la montaña.**

## 3. La pista y SGD (10 min)

- Un **optimizador** es una función que recibe las pendientes y decide cómo mover los pesos.
- SGD es lo que ya hacían: `peso −= eta · pendiente`. («Estocástico» porque usa lotes al azar.)
- Para que la carrera sea rápida: 20 000 imágenes, 5 épocas.

## 4. Momentum (25 min)

Analogía: una **pelota** que rueda cuesta abajo acumula velocidad.
- Si la pendiente apunta siempre al mismo lado, la velocidad crece → **acelera** en las bajadas largas.
- Si cambia de lado a cada rato (zigzag), los empujones se **cancelan** → se **suaviza**.

$$v \leftarrow \beta\, v - \eta \cdot \text{pendiente} \qquad \text{peso} \leftarrow \text{peso} + v$$

`β = 0.9` → «recuerdo el 90 % de mi velocidad anterior». En el pizarrón: con pendiente constante 1 y `eta = 0.01`, la velocidad va 0.01, 0.019, 0.027… hasta 0.1: **10 veces más rápido** que SGD.

**Error típico:** escribir `memoria[k] = v` antes de calcular el nuevo `v`, o sumar `-v`.

## 5. Decaimiento de la tasa (15 min)

Analogía: estacionar el auto. Lejos, vas rápido; cerca, despacio para no chocar.

$$\eta_{\text{época}} = \frac{\eta_0}{1 + k \cdot \text{época}}$$

Con `eta0 = 0.3, k = 1`: 0.3, 0.15, 0.1, 0.075…

## 6. ¡La carrera! (30 min)

Resultados esperados (20 000 imágenes, 5 épocas):

| Corredor | Error final | Precisión |
|---|---|---|
| SGD (eta 0.01) | ~0.38 | ~90 % |
| Momentum (eta 0.01) | ~0.15 | ~95 % |
| Decaimiento (eta0 0.3) | ~0.11 | ~96 % |

Pregunta clave: *¿por qué momentum le gana a SGD con el **mismo** eta?* Y: *¿no sería igual usar SGD con eta más grande?* → Que lo prueben (sección 6): con `eta=0.5` funciona bien; con `eta=2.0` se rompe. Momentum da velocidad **sin** volverse inestable.

Experimentos en grupos (sección 6): `beta=0.99`, SGD con distintos `eta`. Cada grupo cuenta el resultado en 1 minuto.

## 7. La red definitiva (15 min)

Momentum con todos los datos y 5 épocas (~40 s): **~97.6 %**. `guardar_pesos` y `python dibujar.py`. Que comparen con la red de la Clase 5.

## 8. Cierre (10 min)

- Optimizador = cómo bajar la montaña; la red y las pendientes no cambian.
- Momentum = velocidad acumulada; decaimiento = pasos que se achican.
- **Adam** (el más usado hoy) combina las dos ideas: momentum + un `eta` propio para cada peso. En PyTorch es una línea: `torch.optim.Adam(...)`.

**Tarea:** terminar `P6`. Desafío: combinar momentum **con** decaimiento en un solo optimizador. ¿Le gana a los tres?
**Refuerzo opcional:** `notebooks/21_opt_gradiente_2d`, `22_opt_momentum`, `23_opt_lr_decay` (curvas de nivel en 2D: muy visuales).
**Próxima clase:** mueve tu dibujo 3 píxeles… y tu red se rompe. Convoluciones.

---

# PARTE C — Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| ❌ «tus funciones de la Clase 5 están listas» | Falta alguna función o tiene `...` | Pegar las 5 funciones del `P5` completo |
| Momentum da `nan` | Signo cambiado (`+ eta * g`) | `v = beta * v - eta * g[k]` y `red[k] += v` |
| Las tres curvas son iguales | El optimizador no usa `memoria` o no cambia `eta` | Revisar los ejercicios 1 y 2 |
| `TypeError: ... missing ... 'epoca'` | La función del optimizador no tiene los 4 parámetros | Firma: `(red, g, memoria, epoca)` |
