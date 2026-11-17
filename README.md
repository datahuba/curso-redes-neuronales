# Curso de Introducción a las Redes Neuronales

Material del curso: guías, notas, prácticas y notebooks para entender cómo funcionan las redes neuronales **por dentro** y programarlas desde cero con Python y NumPy.

## Contenido

| Carpeta / archivo | Qué contiene |
|---|---|
| [`proyecto/`](proyecto/) | **El curso es un proyecto:** construir desde cero un reconocedor de dígitos escritos a mano. Un notebook por clase (`P1` … `P7`) y `dibujar.py`, una ventana para dibujar números y que tu red los lea |
| [`entregables/`](entregables/) | Guías y diapositivas de cada clase (PDF y PowerPoint) y el curso completo en un PDF |
| [`docs/GUIA_PASO_A_PASO_CLASE1.md`](docs/GUIA_PASO_A_PASO_CLASE1.md) | Clase 1: instalación paso a paso, los datos (MNIST) y una primera IA con plantillas (82 %) |
| [`docs/GUIA_PASO_A_PASO_CLASE2.md`](docs/GUIA_PASO_A_PASO_CLASE2.md) | Clase 2: una neurona (perceptrón) que aprende de sus errores |
| [`docs/GUIA_PASO_A_PASO_CLASE3.md`](docs/GUIA_PASO_A_PASO_CLASE3.md) | Clase 3: sigmoide y descenso por gradiente |
| [`docs/GUIA_PASO_A_PASO_CLASE4.md`](docs/GUIA_PASO_A_PASO_CLASE4.md) | Clase 4: 10 neuronas con softmax (92 %) y ¡a dibujar! |
| [`docs/GUIA_PASO_A_PASO_CLASE5.md`](docs/GUIA_PASO_A_PASO_CLASE5.md) | Clase 5: capa oculta y retropropagación (97 %) |
| [`docs/GUIA_PASO_A_PASO_CLASE6.md`](docs/GUIA_PASO_A_PASO_CLASE6.md) | Clase 6: optimizadores (momentum, decaimiento de la tasa) |
| [`docs/GUIA_PASO_A_PASO_CLASE7.md`](docs/GUIA_PASO_A_PASO_CLASE7.md) | Clase 7: redes convolucionales, aumento de datos y cierre del proyecto |
| [`docs/CURSO.md`](docs/CURSO.md) | Índice del curso: módulos, lecturas y notebooks |
| [`docs/01_Introduccion.md`](docs/01_Introduccion.md) | Módulo 1: motivación, IA y aprendizaje automático |
| [`docs/02_Principios.md`](docs/02_Principios.md) | Módulo 2: McCulloch-Pitts y perceptrón |
| [`docs/practica_02.py`](docs/practica_02.py) | Práctica en Python puro: McCulloch-Pitts y perceptrón (AND, OR, XOR) |
| `docs/practica_03.py` … `docs/practica_07.py` | Prácticas de las clases 3 a 7 (añadir `--graficar` para ver las gráficas) |
| [`notebooks/`](notebooks/) | 17 ejercicios de apoyo en Jupyter (opcionales, para reforzar cada tema) |
| [`docs/guias_notebooks/`](docs/guias_notebooks/README.md) | **Una guía paso a paso por cada notebook**, con pistas y valores para comprobar (PDF en `entregables/`) |
| [`tools/`](tools/) | Scripts que generan los notebooks del proyecto (`build_proyecto.py`), las diapositivas (`build_decks.py`, `export_pdf.ps1`) y los PDF (`md_to_pdf.py`, `build_curso_pdf.py`) |

## Inicio rápido

```bash
conda create --name nni python=3.11
```
```bash
conda activate nni
```
```bash
git clone https://github.com/datahuba/curso-redes-neuronales.git
```
```bash
cd curso-redes-neuronales
```
```bash
pip install -r requirements.txt
```

Después abre la carpeta del repositorio en VS Code, entra a `proyecto/` y abre `P1_conocer_los_datos.ipynb` con el kernel `nni`.

¿Sin Python instalado? Abre cualquier notebook en [Google Colab](https://colab.research.google.com): **Archivo → Abrir cuaderno → GitHub** → `datahuba/curso-redes-neuronales`.

Guía detallada: [docs/GUIA_PASO_A_PASO_CLASE1.md](docs/GUIA_PASO_A_PASO_CLASE1.md).

## Créditos y licencias

Este curso se basa en el trabajo del **Dr. J. Irving Vasquez** ([jivg.org](https://jivg.org)):

- **Notebooks** de `notebooks/`: tomados de [irvingvasquez/cv2course_intro_nn](https://github.com/irvingvasquez/cv2course_intro_nn), con licencia [CC BY 4.0](notebooks/LICENSE-CC-BY-4.0). Se incluyen sin la carpeta de soluciones.
- **Libro** de referencia: [Redes Neuronales](https://irvingvasquez.github.io/libro_redes_neuronales/), con licencia CC BY-NC 4.0. Se enlaza, no se redistribuye.
- **Curso original** y videos: [jivg.org/courses/introduccion-a-las-redes-neuronales-2](https://jivg.org/courses/introduccion-a-las-redes-neuronales-2/).
