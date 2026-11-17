# Guía paso a paso — Clase 7: Redes convolucionales y cierre del proyecto

**Proyecto:** reconocedor de dígitos escritos a mano, en Python y NumPy.
**Pieza de hoy:** **filtros convolucionales** + max-pooling + **aumento de datos**. Una red convolucional que llega a ~97 % con solo 20 000 imágenes y, con aumento de datos, **resiste dibujos movidos**: 81 % contra el 17 % de la red densa.
**Problema que resolvemos:** si mueves el dibujo 3 píxeles, la red densa se derrumba (de 97 % a 17 %). Aprendió *dónde* hay tinta, no *qué forma* tiene.
**Duración:** ~2 h de clase, más 15–30 min de margen para dudas
**Material:** diapositivas `Clase7_Diapositivas` · notebook `proyecto/P7_convolucion.ipynb`

## Objetivos de la clase

Al terminar, cada alumno podrá:
1. Explicar la **convolución** como «la misma lupa recorriendo toda la imagen» y programarla.
2. Explicar qué hacen el **max-pooling** y el **aumento de datos**.
3. Entrenar una red convolucional pequeña y compararla con la red densa.
4. Reconocer en código de PyTorch las piezas que programó a mano durante el curso.

## Agenda

> **Cómo se da esta clase:** directo a la práctica. Los alumnos abren el notebook en el minuto 2 y la teoría entra en **pausas cortas** (⏸) justo cuando el ejercicio la necesita. Regla de oro: **primero lo hacen, después lo explicas** (o, si hace falta para poder hacerlo, lo explicas en 3–5 minutos y vuelven al teclado). Las diapositivas siguen el mismo orden: «Paso» (oscuras) = trabajan; «Pausa · teoría» (claras) = explicas.

| Tiempo | Qué pasa |
|---|---|
| 0:00 | Abrir `P7` y apostar: ¿cuánto baja si muevo el dibujo? (3 min) |
| 0:03 | **Paso 1** · Mover el dibujo 3 píxeles (10 min) |
| 0:13 | **Paso 2** · La convolución a mano (15 min) |
| 0:28 | ⏸ Pausa: una lupa que recorre la imagen (5 min) |
| 0:33 | ⏸ Pausa: nuestra red convolucional (4 min) |
| 0:37 | **Paso 3** · Armar y entrenar la red (20 min) |
| 0:57 | Descanso (10 min) |
| 1:07 | ⏸ Pausa: ¿y si le enseñamos ejemplos movidos? (3 min) |
| 1:10 | **Paso 4** · Aumento de datos (25 min) |
| 1:35 | Cierre del curso: PyTorch, el mapa completo y el proyecto final (25 min) |

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

**Docente:** ejecuta `notebooks_resueltos/proyecto/P7_convolucion.ipynb` (~2 min).

**Importante:** la sección 1 usa el `pesos.npz` de la Clase 5 o 6. Quien no lo tenga: ejecutar antes su `P6` (sección 7) o su `P5`.

---

# PARTE B — La clase paso a paso

## Arranque (3 min)
Abren `proyecto/P7_convolucion.ipynb` (necesitan su `pesos.npz` de la Clase 5 o 6). Antes de ejecutar, **que apuesten**: *si muevo todos los dígitos 3 píxeles, ¿cuánto bajará su 97 %?*

## Paso 1 · Mover el dibujo (10 min)
**Haz:** sección 1. **Deben ver:** ~97.6 % con las originales y **~17 %** con las movidas.
**Explica en 1 minuto:** la red densa tiene un peso distinto para cada píxel: aprendió *dónde* suele haber tinta, no *qué forma* tiene el número. No sabe que los píxeles vecinos están relacionados.

## Paso 2 · La convolución a mano (15 min)
**Haz:** Ejercicio 1 (la fórmula está en el notebook) y mirar los tres filtros (bordes verticales, horizontales, desenfoque).
**Deben ver:** `✅ la convolución suma 9 productos` y las tres imágenes filtradas.

## ⏸ Pausa: una lupa que recorre la imagen (5 min)
Sobre lo que hicieron: el filtro 3 × 3 es una **lupa** que busca una sola cosa; en cada posición multiplica y suma → un mapa de dónde la encontró.
- Pizarrón: filtro de bordes verticales sobre un recorte claro|oscuro → número grande; zona pareja → 0.
- **El mismo filtro en todas partes:** si detecta una curva arriba, también abajo. Y son 9 pesos en vez de 784.
- **La gran idea:** la red **aprende** los 9 números del filtro.

## ⏸ Pausa: nuestra red convolucional (4 min)
- **Recortes:** todos los 3 × 3 como filas de 9 y un solo `@` (así lo hacen las librerías).
- **Max-pooling 2 × 2:** el máximo de cada cuadrito; achica y tolera movimientos chicos.
- Arquitectura: `28×28 → 8 filtros + ReLU → 26×26×8 → pooling → 13×13×8 = 1352 → 10`.

## Paso 3 · Armar y entrenar la red (20 min)
**Haz:** Ejercicio 2 (pase hacia adelante) y entrenar (~1 min).
**Mientras entrena**, explica los dos detalles nuevos de la retropropagación (comentados en el código): en el pooling solo el **ganador** recibe culpa; el filtro **suma** su pendiente de las 676 posiciones.
**Deben ver:** ~97 % con las originales y ~23 % con las movidas. *¿Decepción?* Mejora un poco pero no alcanza: la capa final todavía aprende posiciones.

## Descanso (10 min)

## ⏸ Pausa: ejemplos movidos (3 min)
*Si quieres que no le importe la posición, ¿qué ejemplos le mostrarías?* → **ejemplos movidos**, fabricados moviendo los que ya tenemos (**aumento de datos**). *¿Qué aumento NO sirve?* Voltear: un 2 volteado ya no es un 2.

## Paso 4 · Aumento de datos (25 min)
**Haz:** Ejercicio 3 (`np.roll` con desplazamiento al azar) y entrenar otra vez.
**Deben ver:**

| Red | Originales | Movidas 3 px |
|---|---|---|
| Densa (Clase 6) | ~97.6 % | ~17 % |
| Convolucional | ~97 % | ~23 % |
| Convolucional + aumento | ~94 % | **~81 %** |

Pierde un poquito con las originales y gana muchísimo con las movidas. Luego la sección 7: los filtros que aprendió parecen **detectores de bordes**, sin que nadie se los diera.

## Cierre del curso (25 min)
1. **PyTorch:** que identifiquen cada línea con lo que programaron (`Conv2d` = sus filtros, `cross_entropy` = su softmax + error, `backward()` = su retropropagación, `SGD(momentum)` = su momentum).
2. **El mapa completo:** que cada uno diga qué pieza le costó más.
3. **Proyecto final** en parejas (medir antes y después, 3 minutos de presentación): más capas, momentum + decaimiento, más aumento (rotaciones), u otros datos (Fashion-MNIST).

**Refuerzo opcional:** `3_1_capa_convolucional`, `3_2_entrenar_capa_conv`.

---

# PARTE C — Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| «No encuentro pesos.npz» | No guardaron pesos en la Clase 5/6 | Ejecutar `P6` o `P5` completo antes |
| `ValueError: cannot reshape` en `max_pool` | `Z` con forma equivocada | `Z = R @ red["F"] + red["bf"]` debe dar `(n, 26, 26, 8)` |
| Entrenar tarda más de 5 minutos | Computadora lenta | Usar `X_train[:10000]` (baja ~1 punto la precisión) |
| `MemoryError` | Poca RAM | Lotes más chicos en `precision(..., lote=500)` y 10 000 imágenes |
| La red con aumento no mejora con las movidas | `mover_al_azar` no mueve (devuelve la misma imagen) | Revisar el `np.roll` con `(dy, dx)` y `axis=(0, 1)` |
