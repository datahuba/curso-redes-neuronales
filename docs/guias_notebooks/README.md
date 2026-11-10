# Guías de los notebooks

Una guía por cada notebook del curso, escrita para alguien que empieza desde cero. Cada guía tiene:
- qué vas a aprender;
- cómo abrir el notebook;
- la teoría mínima, explicada con palabras simples;
- un recorrido **celda por celda**, con pistas para cada `TODO` y **valores para comprobar** tu resultado (salen de ejecutar el notebook de verdad);
- respuestas orientativas a las preguntas del notebook;
- una tabla de errores frecuentes.

Las guías **no** dan el código de la solución: dan pistas y resultados para comprobar.

| # | Notebook | Tema | Clase | Puntos | Guía |
|---|---|---|---|---|---|
| 1 | `1_01_mcculloch_pitts` | Neurona de McCulloch y Pitts | 2 | 3 | [Guía](NB_1_01_mcculloch_pitts.md) |
| 2 | `1_02_perceptron_AND` | Perceptrón: pesos a mano para AND | 2 | práctica | [Guía](NB_1_02_perceptron_AND.md) |
| 3 | `1_03_1_perceptron_simple` | Perceptrón simple en Python | 2 | 3 | [Guía](NB_1_03_1_perceptron_simple.md) |
| 4 | `1_03_2_regla_de_aprendizaje` | Regla de aprendizaje de Rosenblatt | 2 | 4 | [Guía](NB_1_03_2_regla_de_aprendizaje.md) |
| 5 | `1_04_red_neuronal_simple` | Neurona con sigmoide y tanh | 3 | 3 | [Guía](NB_1_04_red_neuronal_simple.md) |
| 6 | `1_05_descenso_por_gradiente_1D` | Descenso por gradiente en una variable | 3 | 2 | [Guía](NB_1_05_descenso_por_gradiente_1D.md) |
| 7 | `1_06_descenso_unpaso` | Un paso de la regla delta | 4 | 3 | [Guía](NB_1_06_descenso_unpaso.md) |
| 8 | `1_07_descenso_por_gradiente` | Entrenar una neurona completa | 4 | 3 | [Guía](NB_1_07_descenso_por_gradiente.md) |
| 9 | `1_08_adaline` | ADALINE: regresión con una neurona | 4 | demostración | [Guía](NB_1_08_adaline.md) |
| 10 | `1_09_red_multicapa_ejercicio` | Red multicapa: pase hacia adelante | 5 | 3 | [Guía](NB_1_09_red_multicapa_ejercicio.md) |
| 11 | `1_10_retropropagacion_base` | Retropropagación: un paso | 5 | 3 | [Guía](NB_1_10_retropropagacion_base.md) |
| 12 | `1_11_retropropagacion_completo` | Entrenar una red multicapa | 5 | 3 | [Guía](NB_1_11_retropropagacion_completo.md) |
| 13 | `21_opt_gradiente_2d` | Descenso por gradiente en 2D | 6 | experimentos | [Guía](NB_21_opt_gradiente_2d.md) |
| 14 | `22_opt_momentum` | Optimizador con momentum | 6 | experimentos | [Guía](NB_22_opt_momentum.md) |
| 15 | `23_opt_lr_decay` | Decaimiento de la tasa de aprendizaje | 6 | 3 | [Guía](NB_23_opt_lr_decay.md) |
| 16 | `3_1_capa_convolucional` | Capa convolucional (correlación cruzada) | 7 | 4 | [Guía](NB_3_1_capa_convolucional.md) |
| 17 | `3_2_entrenar_capa_conv` | Reto: entrenar un kernel convolucional | 7 | reto | [Guía](NB_3_2_entrenar_capa_conv.md) |

Las clases 5 a 7 todavía no tienen guía de clase ni diapositivas. La columna indica en qué orden conviene hacer los notebooks.

## Antes de cualquier notebook

Necesitas el ambiente `nni` y el repositorio descargado: [Guía de la Clase 1](../GUIA_PASO_A_PASO_CLASE1.md), Parte A. Cada guía repite en corto cómo abrir su notebook.

## Cambios respecto a los notebooks originales
- **`23_opt_lr_decay`:** en el repositorio original está **vacío**. Este curso incluye uno nuevo, en el mismo estilo que los notebooks 21 y 22.
- **`1_03_2_regla_de_aprendizaje`:** se agregó `n_classes=2` en las dos gráficas, porque scikit-learn 1.9 lo exige.
- **`notebooks/output/`:** carpeta nueva, donde `1_05` guarda su gráfica.
