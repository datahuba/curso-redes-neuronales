# Curso: Introducción a las Redes Neuronales — Índice

Material del Dr. J. Irving Vasquez (jivg.org):
- **Libro** (CC BY-NC 4.0): https://irvingvasquez.github.io/libro_redes_neuronales/
- **Notebooks** (CC BY 4.0): https://github.com/irvingvasquez/cv2course_intro_nn — copia en `notebooks/` (sin soluciones)

Para preparar el entorno de los notebooks:

```bash
pip install -r requirements.txt
```

| Módulo | Mis notas | Libro (capítulos en línea) | Notebooks (../notebooks/…) |
|---|---|---|---|
| 1. Introducción (clase 1) | [Guía clase 1](GUIA_PASO_A_PASO_CLASE1.md), [01_Introduccion.md](01_Introduccion.md) | `01-introduccion/*`, `02-preliminares/06-aprendizaje-automatico` | — |
| 0. Preliminares (opcional) | — | `02-preliminares/02…09` (Python, álgebra, cálculo, probabilidad, optimización, gradiente) | `21_opt_gradiente_2d` |
| 2. Principios: McCulloch-Pitts y perceptrón (clase 2) | [Guía clase 2](GUIA_PASO_A_PASO_CLASE2.md), [02_Principios.md](02_Principios.md), [practica_02.py](practica_02.py) | `03-fundamentos/01…03`, `04-aprendizaje/02-regla-de-aprendizaje-del-perceptron` | `1_01_mcculloch_pitts`, `1_02_perceptron_AND`, `1_03_1_perceptron_simple`, `1_03_2_regla_de_aprendizaje` |
| 3. Red neuronal simple y descenso por gradiente (clases 3 y 4) | [Clase 3](GUIA_PASO_A_PASO_CLASE3.md), [Clase 4](GUIA_PASO_A_PASO_CLASE4.md), [practica_03.py](practica_03.py), [practica_04.py](practica_04.py) | `03-fundamentos/04-neurona-artificial-moderna`, `05-redes-de-varias-salidas`, `04-aprendizaje/03-descenso-por-gradiente` | `1_04_red_neuronal_simple`, `1_05_descenso_por_gradiente_1D`, `1_06_descenso_unpaso`, `1_07_descenso_por_gradiente`, `1_08_adaline` |
| 4. Redes multicapa y retropropagación (clase 5) | [Guía clase 5](GUIA_PASO_A_PASO_CLASE5.md), [practica_05.py](practica_05.py), [guías de notebooks](guias_notebooks/README.md) | `03-fundamentos/06-redes-neuronales-multicapa`, `04-aprendizaje/04-retropropagacion` | `1_09_red_multicapa_ejercicio`, `1_10_retropropagacion_base`, `1_11_retropropagacion_completo`  |
| 5. Optimización práctica (clase 6) | [Guía clase 6](GUIA_PASO_A_PASO_CLASE6.md), [practica_06.py](practica_06.py), [guías de notebooks](guias_notebooks/README.md) | `02-preliminares/08-optimizacion` | `22_opt_momentum`, `23_opt_lr_decay` (nuevo: el original está vacío) |
| 6. Puente a redes profundas: convolución (clase 7) | [Guía clase 7](GUIA_PASO_A_PASO_CLASE7.md), [practica_07.py](practica_07.py), [guías de notebooks](guias_notebooks/README.md) | — | `3_1_capa_convolucional`, `3_2_entrenar_capa_conv` |
| Resúmenes | — | `03-fundamentos/07-acordeon…`, `04-aprendizaje/05-acordeon…` | — |

Las guías, diapositivas (PDF y PowerPoint) y PDFs de cada clase están en [`entregables/`](../entregables/). Cada notebook tiene además su propia guía paso a paso en [`guias_notebooks/`](guias_notebooks/README.md).

**Orden sugerido:** cada módulo → leer el capítulo del libro → mis notas → resolver el notebook.
