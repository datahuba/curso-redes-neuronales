# Guía paso a paso — Clase 6: Entrenar más rápido y mejor (optimizadores)

**Proyecto:** reconocedor de dígitos escritos a mano, en Python y NumPy.
**Pieza de hoy:** **momentum** y **decaimiento de la tasa de aprendizaje**, comparados en una **carrera** con la misma red. La red definitiva llega a **~97.6 %**.
**Problema que resolvemos:** con descenso por gradiente simple, si `eta` es chico tarda una eternidad y si es grande rebota.
**Duración:** ~2 h de clase, más 15–30 min de margen para dudas
**Material:** diapositivas `Clase6_Diapositivas` · notebook `proyecto/P6_entrenar_mejor.ipynb`

## Objetivos de la clase

Al terminar, cada alumno podrá:
1. Explicar qué es un **optimizador** y por qué es independiente de la red.
2. Programar **momentum** y **decaimiento de la tasa** y explicarlos con analogías.
3. Comparar optimizadores con sus curvas de aprendizaje y elegir uno con argumentos.

## Agenda

> **Cómo se da esta clase:** directo a la práctica. Los alumnos abren el notebook en el minuto 2 y la teoría entra en **pausas cortas** (⏸) justo cuando el ejercicio la necesita. Regla de oro: **primero lo hacen, después lo explicas** (o, si hace falta para poder hacerlo, lo explicas en 3–5 minutos y vuelven al teclado). Las diapositivas siguen el mismo orden: «Paso» (oscuras) = trabajan; «Pausa · teoría» (claras) = explicas.

| Tiempo | Qué pasa |
|---|---|
| 0:00 | Abrir `P6` y la misión de hoy (3 min) |
| 0:03 | **Paso 1** · Traer tu red de la Clase 5 y correr SGD (15 min) |
| 0:18 | ⏸ Pausa: momentum, la pelota que rueda (5 min) |
| 0:23 | ⏸ Pausa: decaimiento de la tasa (3 min) |
| 0:26 | **Paso 2** · Programar los dos corredores (20 min) |
| 0:46 | Descanso (10 min) |
| 0:56 | **Paso 3** · ¡La carrera! (15 min) |
| 1:11 | **Paso 4** · Experimentos y red definitiva + dibujar (40 min) |
| 1:51 | Mapa y cierre: Adam y lo que viene (10 min) |

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

## Arranque (3 min)
Abren `proyecto/P6_entrenar_mejor.ipynb`. Misión: *una carrera entre formas de bajar la montaña, y la red definitiva. La red no cambia: solo cómo la entrenamos.*

## Paso 1 · Traer tu red y correr SGD (15 min)
**Haz:** pegar `relu`, `softmax`, `crear_red`, `adelante` y `gradientes` de **su** `P5`; ejecutar la pista de carreras y el corredor SGD.
**Deben ver:** `✅ tus funciones de la Clase 5 están listas`.
**Si alguien no terminó el P5:** que copie las funciones de un compañero.

## ⏸ Pausa: momentum (5 min)
Dibuja un valle **alargado** (una canaleta): la pendiente apunta a las paredes → **zigzag**. Así son los errores de las redes reales.
Analogía: una **pelota** que rueda acumula velocidad: si la pendiente apunta siempre al mismo lado, **acelera**; si cambia de lado (zigzag), los empujones se **cancelan**.
`v ← βv − η·pendiente`, `peso ← peso + v`. Con β = 0.9 «recuerdo el 90 % de mi velocidad». Pendiente constante 1 y η 0.01: 0.01, 0.019, 0.027… hasta 0.1 → **10 veces más rápido**.

## ⏸ Pausa: decaimiento (3 min)
Como estacionar: lejos, rápido; cerca, despacio. `η = η₀ / (1 + k·época)` → 0.3, 0.15, 0.1, 0.075…

## Paso 2 · Programar los dos corredores (20 min)
**Haz:** Ejercicios 1 (momentum) y 2 (decaimiento).
**Errores típicos:** sumar `-v`; guardar `memoria[k] = v` antes de calcular el nuevo `v`; signo cambiado (`+ eta * g`) → `nan`.

## Descanso (10 min)

## Paso 3 · ¡La carrera! (15 min)
**Haz:** sección 5. **Deben ver** (20 000 imágenes, 5 épocas):

| Corredor | Error final | Precisión |
|---|---|---|
| SGD (eta 0.01) | ~0.38 | ~90 % |
| Momentum (eta 0.01) | ~0.15 | ~95 % |
| Decaimiento (eta0 0.3) | ~0.11 | ~96 % |

**Pregunta:** *¿por qué momentum le gana a SGD con el **mismo** eta? ¿No sería igual SGD con eta más grande?* → lo prueban en el paso 4.

## Paso 4 · Experimentos y red definitiva (40 min)
**Haz:** sección 6 en grupos (SGD con `eta` 0.5 y 2.0; momentum con `beta=0.99`), cada grupo cuenta su resultado en 1 minuto. Después sección 7: la red definitiva con momentum y todos los datos (~40 s).
**Deben ver:** `Precisión de la red definitiva: 97.64%`. Y `python dibujar.py` para compararla con la de la Clase 5.
**Conclusión:** momentum da velocidad **sin** volverse inestable (SGD con `eta=2.0` se rompe).

## Cierre (10 min)
- Optimizador = cómo bajar la montaña; red y pendientes no cambian.
- **Adam** (el más usado hoy) combina las dos ideas: momentum + un `eta` propio para cada peso. En PyTorch es una línea.
- **Tarea:** terminar `P6`. Desafío: momentum + decaimiento juntos.
- **Refuerzo opcional:** `21`, `22`, `23` (curvas de nivel en 2D).
- **Próxima clase:** mueve tu dibujo 3 píxeles… y la red se rompe.

---

# PARTE C — Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| ❌ «tus funciones de la Clase 5 están listas» | Falta alguna función o tiene `...` | Pegar las 5 funciones del `P5` completo |
| Momentum da `nan` | Signo cambiado (`+ eta * g`) | `v = beta * v - eta * g[k]` y `red[k] += v` |
| Las tres curvas son iguales | El optimizador no usa `memoria` o no cambia `eta` | Revisar los ejercicios 1 y 2 |
| `TypeError: ... missing ... 'epoca'` | La función del optimizador no tiene los 4 parámetros | Firma: `(red, g, memoria, epoca)` |
