# Guía paso a paso — Clase 7: Redes convolucionales y cierre del proyecto

**Proyecto:** reconocedor de dígitos escritos a mano, en Python y NumPy.
**Pieza de hoy:** **filtros convolucionales** + max-pooling + **aumento de datos**. Una red convolucional que llega a ~97 % con solo 20 000 imágenes y, con aumento de datos, **resiste dibujos movidos**: 81 % contra el 17 % de la red densa.
**Problema que resolvemos:** si mueves el dibujo 3 píxeles, la red densa se derrumba (de 97 % a 17 %). Aprendió *dónde* hay tinta, no *qué forma* tiene.
**Duración:** ~2 h 30 min
**Material:** diapositivas `Clase7_Diapositivas` · notebook `proyecto/P7_convolucion.ipynb`

## Objetivos de la clase

Al terminar, cada alumno podrá:
1. Explicar la **convolución** como «la misma lupa recorriendo toda la imagen» y programarla.
2. Explicar qué hacen el **max-pooling** y el **aumento de datos**.
3. Entrenar una red convolucional pequeña y compararla con la red densa.
4. Reconocer en código de PyTorch las piezas que programó a mano durante el curso.

## Agenda

| Tiempo | Tema |
|---|---|
| 0:00 | El experimento que rompe la red, notebook `P7` sección 1 (15 min) |
| 0:15 | La convolución: Ejercicio 1 y filtros a mano (25 min) |
| 0:40 | La versión rápida y la red convolucional, Ejercicio 2 (25 min) |
| 1:05 | Descanso (10 min) |
| 1:15 | Entrenar (mientras corre: explicar la retropropagación nueva) (15 min) |
| 1:30 | Aumento de datos, Ejercicio 3 (25 min) |
| 1:55 | Los filtros aprendidos (10 min) |
| 2:05 | Cierre del curso: lo mismo en PyTorch y el recorrido completo (25 min) |

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

## 1. El experimento (15 min)

Antes de ejecutar, pregunta: *si muevo todos los dígitos 3 píxeles a la derecha y abajo, ¿cuánto bajará la precisión de su red de 97 %?* Que apuesten. Luego ejecutan: **~17 %**.

Explicación: la red densa tiene un peso **distinto** para cada píxel. Aprendió «en el píxel 300 suele haber tinta si es un 1». Si el 1 se corre, ese píxel queda vacío. **No sabe que los píxeles vecinos están relacionados.**

## 2. La convolución (25 min)

Analogía: una **lupa** de 3 × 3 que recorre la imagen buscando **una sola cosa** (por ejemplo, un borde vertical). En cada posición: multiplica casilla por casilla, suma, anota un número. Resultado: un **mapa** de dónde encontró esa cosa.

- Ejemplo en el pizarrón con un recorte 3 × 3 y el filtro de bordes verticales `[[1,0,−1],[2,0,−2],[1,0,−1]]`: a la izquierda claro y a la derecha oscuro da un número grande; en una zona pareja da 0.
- **El mismo filtro en todas las posiciones** → si detecta una curva arriba, también la detecta abajo. Y usa solo 9 pesos en vez de 784.
- La salida es 26 × 26 porque la lupa no cabe en el borde.

Ejercicio 1 y las tres imágenes filtradas (bordes verticales, horizontales, desenfoque).

**Idea clave:** en una red convolucional **los 9 números del filtro son pesos que se aprenden** con descenso por gradiente.

## 3. Versión rápida y la red (25 min)

- **Recortes:** sacar todos los recortes 3 × 3 como filas de 9 números y hacer `recortes @ filtros`. Es la misma cuenta, pero con un solo `@`: así lo hacen las librerías de verdad.
- **Max-pooling 2 × 2:** de cada cuadrito nos quedamos con el máximo. «¿Hay un borde por acá? Sí/no»: reduce el tamaño a la mitad y tolera movimientos chicos.
- Arquitectura: `28×28 → 8 filtros + ReLU → 26×26×8 → pooling → 13×13×8 = 1352 → 10`.

Ejercicio 2 (pase hacia adelante): mismas piezas de siempre, en otro orden.

## 4. Entrenar (15 min)

Mientras entrena (~1 min), explica los **dos detalles nuevos** de la retropropagación (están comentados en el código):
1. En el max-pooling solo el **ganador** de cada cuadrito recibe culpa (los demás no influyeron).
2. El filtro se usó en las 676 posiciones → su pendiente es la **suma** de las 676.

Resultado: ~97 % con solo 20 000 imágenes y 8 filtros. Con las movidas: ~23 %. *¿Decepción?* Mejora un poco, pero **no alcanza**: la capa densa del final sigue aprendiendo posiciones.

## 5. Aumento de datos (25 min)

Pregunta: *si quieres que no le importe la posición, ¿qué ejemplos le mostrarías?* → **Ejemplos movidos.** No hace falta conseguir datos nuevos: se fabrican moviendo los que ya hay.

Ejercicio 3 (`np.roll` con desplazamiento al azar). Resultado esperado:

| Red | Originales | Movidas 3 px |
|---|---|---|
| Densa (Clase 6) | ~97.6 % | ~17 % |
| Convolucional | ~97 % | ~23 % |
| Convolucional + aumento | ~94 % | **~81 %** |

Para comentar: pierde un poco con las originales y gana muchísimo con las movidas. *¿Qué otros aumentos tienen sentido para dígitos?* (rotar un poco, engrosar el trazo, ruido). *¿Y cuál NO?* (voltear horizontalmente: un 2 volteado ya no es un 2).

## 6. Los filtros aprendidos (10 min)

Arriba los 8 filtros (3 × 3) y abajo qué detectan en un dígito. Muchos se parecen a **detectores de bordes** en distintas direcciones, **sin que nadie se los diera**.

## 7. Cierre del curso (25 min)

1. **Lo mismo en PyTorch** (sección 9 del notebook): que identifiquen cada línea con lo que programaron: `Conv2d` = sus filtros, `cross_entropy` = su softmax + error, `backward()` = su retropropagación, `SGD(momentum=0.9)` = su momentum.
2. **El recorrido completo:** la tabla de precisiones de la Clase 1, ahora completa. Que cada uno diga qué pieza le costó más.
3. **Qué sigue:** más capas convolucionales (redes profundas), PyTorch, otros datos (ropa: Fashion-MNIST; letras; fotos).

**Proyecto final sugerido** (en parejas, para entregar): elegir una mejora, medirla y presentarla en 3 minutos.
- Dos capas ocultas en la red densa.
- Momentum + decaimiento juntos.
- Más filtros o una segunda capa convolucional.
- Aumento con rotaciones.
- Entrenar con Fashion-MNIST (cambiando la URL en `digitos.py`).

**Refuerzo opcional:** `notebooks/3_1_capa_convolucional` y `3_2_entrenar_capa_conv`.

---

# PARTE C — Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| «No encuentro pesos.npz» | No guardaron pesos en la Clase 5/6 | Ejecutar `P6` o `P5` completo antes |
| `ValueError: cannot reshape` en `max_pool` | `Z` con forma equivocada | `Z = R @ red["F"] + red["bf"]` debe dar `(n, 26, 26, 8)` |
| Entrenar tarda más de 5 minutos | Computadora lenta | Usar `X_train[:10000]` (baja ~1 punto la precisión) |
| `MemoryError` | Poca RAM | Lotes más chicos en `precision(..., lote=500)` y 10 000 imágenes |
| La red con aumento no mejora con las movidas | `mover_al_azar` no mueve (devuelve la misma imagen) | Revisar el `np.roll` con `(dy, dx)` y `axis=(0, 1)` |
