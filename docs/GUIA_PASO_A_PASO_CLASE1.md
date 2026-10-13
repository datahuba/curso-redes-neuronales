# Guía paso a paso — Clase 1: Introducción a las Redes Neuronales

Esta guía explica **todo** lo que aparece en las 16 diapositivas, desde cero, como si nunca hubieras visto el tema. Tiene tres partes:

- **Parte A:** preparar las computadoras ANTES de clase (instalación rigurosa, con verificación en cada paso).
- **Parte B:** qué explicar en cada diapositiva, con definiciones sencillas y ejemplos.
- **Parte C:** problemas frecuentes y cómo resolverlos.

Diapositivas: https://claude.ai/artifact/9vRb7zDTg2JWdN1B1YQL4j

---

# PARTE A — Preparar las computadoras (hazlo antes de clase)

## A.0 Conceptos mínimos antes de instalar

| Palabra | Qué es, en simple |
|---|---|
| **Python** | El lenguaje de programación que usaremos. |
| **Paquete / librería** | Código que otros ya escribieron y que instalamos para usarlo. Ejemplo: **NumPy** sirve para hacer cuentas con vectores y matrices. |
| **Anaconda / conda** | Programa que instala Python y administra "ambientes". |
| **Ambiente** | Una "caja" aislada con su propia versión de Python y sus paquetes. Así un proyecto no rompe a otro. El nuestro se llamará `nni` (*neural network introduction*). |
| **pip** | El instalador de paquetes de Python. |
| **Terminal** | Ventana donde se escriben comandos de texto. Usaremos **Anaconda PowerShell Prompt** y **Git Bash**. |
| **Git** | Programa para descargar y versionar código. |
| **GitHub** | Sitio web donde se guarda código. Allí está el repositorio del curso. |
| **Repositorio (repo)** | Carpeta de un proyecto con todos sus archivos. |
| **Clonar** | Descargar un repositorio a tu computadora con Git. |
| **Notebook (.ipynb)** | Documento que mezcla texto y celdas de código que se ejecutan una por una. Los ejercicios vienen así. |
| **Jupyter** | El programa que ejecuta los notebooks. |
| **VS Code** | Editor de código donde abriremos los notebooks. |
| **Kernel** | El "motor" de Python que ejecuta las celdas de un notebook. Debemos elegir el de nuestro ambiente `nni`. |

**Regla de oro:** después de cada paso hay una **verificación**. No avances si la verificación falla; ve a la Parte C.

## A.1 Elegir el camino

| Camino | Cuándo usarlo | Qué necesita |
|---|---|---|
| **Camino 1: Google Colab** | Computadoras sin permisos para instalar, poco tiempo o plan B | Navegador y cuenta de Google |
| **Camino 2: Instalación local** | Es lo recomendado en el curso: da experiencia real de desarrollo | Instalar Anaconda, Git y VS Code (unos 40 minutos y unos 5 GB libres) |

Recomendación: prepara el **Camino 2** en tu computadora y ten listo el **Camino 1** como respaldo para los alumnos que tengan problemas.

---

## A.2 Camino 1 — Google Colab (sin instalar nada)

1. Abre el navegador y entra a: https://github.com/datahuba/curso-redes-neuronales y abre la carpeta `notebooks`
2. Haz clic en un notebook, por ejemplo `1_01_mcculloch_pitts.ipynb`.
3. Si aparece el botón **"Open in Colab"**, haz clic. Si no aparece:
   1. Entra a https://colab.research.google.com
   2. Menú **Archivo → Abrir cuaderno**.
   3. Elige la pestaña **GitHub**.
   4. Pega `datahuba/curso-redes-neuronales` y presiona Enter.
   5. Elige el notebook.
4. Inicia sesión con tu cuenta de Google si lo pide.
5. Haz clic en la primera celda de código y presiona **Shift + Enter** para ejecutarla.
6. Para guardar tus cambios: **Archivo → Guardar una copia en Drive**. Si no lo haces, se pierden.

**Verificación:** crea una celda nueva (botón **+ Código**), escribe esto y ejecútala:

```python
import numpy as np
print(np.__version__)
```

Si aparece un número de versión (por ejemplo `1.26.4`), Colab funciona.

**Notebooks que usan la carpeta `nni`** (como `1_03_2`): en Colab necesitan el repositorio completo. Ejecuta en la primera celda:

```python
!git clone https://github.com/datahuba/curso-redes-neuronales
%cd curso-redes-neuronales/notebooks
```

---

## A.3 Camino 2 — Instalación local en Windows

Sigue los pasos **en orden**. En total son 7.

### Paso 1. Instalar Anaconda

1. Entra a https://www.anaconda.com/download
2. Descarga el instalador para **Windows**, el botón de 64 bits.
3. Ejecuta el archivo descargado (`Anaconda3-...-Windows-x86_64.exe`).
4. En el instalador:
   - **Next → I Agree**.
   - Elige **Just Me (recommended)**.
   - Deja la carpeta que propone. Es importante que la ruta no tenga espacios ni acentos; normalmente es `C:\Users\TuUsuario\anaconda3`.
   - En opciones avanzadas, deja marcadas las que vienen por defecto. **No** marques "Add Anaconda to my PATH".
   - **Install** y espera de 5 a 15 minutos → **Finish**.

**Verificación:**
1. Abre el menú Inicio y escribe `Anaconda PowerShell Prompt`. Ábrelo.
2. Debe verse una línea que empieza con `(base)`, por ejemplo:
   ```
   (base) PS C:\Users\TuUsuario>
   ```
3. Escribe y presiona Enter:
   ```bash
   conda --version
   ```
   Debe responder algo como `conda 24.x.x`.

> Nota del curso: Anaconda tiene una interfaz gráfica (Anaconda Navigator), pero es lenta. Usaremos la terminal.

### Paso 2. Crear el ambiente `nni`

En la misma ventana de **Anaconda PowerShell Prompt** escribe:

```bash
conda create --name nni python=3.11
```

Qué significa:
- `conda create` → crea un ambiente nuevo.
- `--name nni` → le pone de nombre `nni`.
- `python=3.11` → le instala Python 3.11.

En el video se usa `python=3`; 3.11 es una versión 3 concreta y estable que funciona con todos los paquetes.

Cuando pregunte `Proceed ([y]/n)?`, escribe `y` y presiona Enter. Descargará e instalará; tarda de 1 a 3 minutos.

**Verificación:**
```bash
conda env list
```
Debe aparecer una línea con `nni` y su ruta.

### Paso 3. Activar el ambiente

```bash
conda activate nni
```

**Verificación:** el inicio de la línea debe cambiar de `(base)` a `(nni)`:
```
(nni) PS C:\Users\TuUsuario>
```

⚠️ **Cada vez que abras una terminal nueva**, el ambiente vuelve a `(base)`. Debes repetir `conda activate nni`.

### Paso 4. Instalar los paquetes

Con `(nni)` visible, escribe (es **una sola línea**):

```bash
pip install jupyter numpy pandas matplotlib scikit-learn pillow ipykernel
```

Para qué sirve cada uno:

| Paquete | Para qué |
|---|---|
| `jupyter` | Ejecutar notebooks |
| `numpy` | Vectores, matrices y cuentas |
| `pandas` | Tablas de datos |
| `matplotlib` | Gráficas |
| `scikit-learn` | Utilidades de aprendizaje automático (el notebook `1_03_2` lo necesita) |
| `pillow` | Abrir imágenes |
| `ipykernel` | Que VS Code reconozca el ambiente como kernel |

Espera a que termine; tarda de 2 a 5 minutos. La última línea debe decir `Successfully installed ...`.

**Verificación:** copia y ejecuta esta línea:

```bash
python -c "import numpy, pandas, matplotlib, sklearn, PIL; print('TODO OK')"
```

Debe imprimir `TODO OK`. Si dice `ModuleNotFoundError`, revisa que estés en `(nni)` y repite el Paso 4.

### Paso 5. Instalar Git for Windows

1. Entra a https://git-scm.com/download/win
2. Descarga **64-bit Git for Windows Setup** y ejecútalo.
3. Acepta todas las opciones por defecto (**Next** en todo) → **Install** → **Finish**.

**Verificación:**
1. Menú Inicio → escribe `Git Bash` → ábrelo. Es una ventana negra con texto de colores.
2. Escribe:
   ```bash
   git --version
   ```
   Debe responder algo como `git version 2.4x.x.windows.1`.

### Paso 6. Clonar el repositorio del curso

En **Git Bash**:

1. Ve a tu carpeta de usuario y crea una carpeta para tus proyectos:
   ```bash
   cd ~
   ```
   ```bash
   mkdir -p projects
   ```
   ```bash
   cd projects
   ```
   - `cd` = cambiar de carpeta.
   - `~` = tu carpeta de usuario.
   - `mkdir -p` = crear la carpeta; si ya existe, no hace nada.
2. Clona el repositorio:
   ```bash
   git clone https://github.com/datahuba/curso-redes-neuronales.git
   ```
   El enlace también se puede copiar desde GitHub: botón verde **Code → copiar**.
3. Entra a la carpeta y lista su contenido:
   ```bash
   cd curso-redes-neuronales
   ```
   ```bash
   ls
   ```

**Verificación:** `ls` debe mostrar las carpetas `notebooks` y `docs` y el archivo `README.md`.

> Si ya existía la carpeta, Git dirá `destination path ... already exists`. No es un error grave: ya lo tienes clonado.
>
> **Alternativa sin Git:** en GitHub, botón verde **Code → Download ZIP**. Luego descomprímelo en `C:\Users\TuUsuario\projects`.

### Paso 7. Instalar VS Code y abrir los notebooks

1. Entra a https://code.visualstudio.com, descarga e instala con las opciones por defecto. Marca **"Agregar a PATH"** si aparece.
2. Abre VS Code.
3. Instala dos extensiones:
   1. Haz clic en el ícono de **Extensiones** de la barra izquierda (cuatro cuadritos) o presiona `Ctrl + Shift + X`.
   2. Busca **Python** (de Microsoft) → **Install**.
   3. Busca **Jupyter** (de Microsoft) → **Install**.
4. **File → Open Folder…** (Archivo → Abrir carpeta) → elige `C:\Users\TuUsuario\projects\curso-redes-neuronales\notebooks` → **Seleccionar carpeta**. Si pregunta si confías en los autores, elige **Yes, I trust**.
5. En el panel izquierdo haz clic en `1_01_mcculloch_pitts.ipynb`.
6. **Elegir el kernel (muy importante):**
   1. Arriba a la derecha haz clic en **Select Kernel**.
   2. Elige **Python Environments…**.
   3. Elige el que diga **nni**, por ejemplo `nni (Python 3.11.x)`.
7. Haz clic en la primera celda de código y presiona **Shift + Enter**.

**Verificación final:** crea una celda (botón **+ Code**), escribe esto y ejecútalo con Shift + Enter:

```python
import sys, numpy as np
print(sys.executable)
print(np.__version__)
```

- La primera línea debe contener `envs\nni` (prueba de que usas el ambiente correcto).
- La segunda debe ser un número de versión.

✅ Si ves ambas cosas, **la computadora está lista**.

### Resumen de comandos (para copiar)

**Anaconda PowerShell Prompt:**
```bash
conda create --name nni python=3.11
```
```bash
conda activate nni
```
```bash
pip install jupyter numpy pandas matplotlib scikit-learn pillow ipykernel
```
```bash
python -c "import numpy, pandas, matplotlib, sklearn, PIL; print('TODO OK')"
```

**Git Bash:**
```bash
cd ~ && mkdir -p projects && cd projects
```
```bash
git clone https://github.com/datahuba/curso-redes-neuronales.git
```

**Alternativa sin VS Code** (desde Anaconda PowerShell con `(nni)` activo):
```bash
cd ~\projects\curso-redes-neuronales\notebooks
```
```bash
jupyter notebook
```
Se abre el navegador con la lista de notebooks. Para cerrarlo, en la terminal presiona `Ctrl + C`.

---

## A.4 Checklist del día de la clase

- [ ] Tu computadora pasó la **Verificación final** del Paso 7.
- [ ] Probaste abrir un notebook en **Colab** (plan B).
- [ ] Tienes abiertas las diapositivas.
- [ ] Llegaste 15 minutos antes para probar el proyector.
- [ ] Si los alumnos instalarán en clase: avísales que traigan laptop con **5 GB libres** y permisos de administrador. Si pueden, que descarguen Anaconda en casa, porque son unos 900 MB.

---

# PARTE B — Qué explicar en cada diapositiva

Duración sugerida: **2 horas**. Junto a cada título va el tiempo aproximado.

## Diapositiva 1 — Portada (2 min)
**Qué decir:** "Este es un curso introductorio. Vamos a entender cómo funcionan las redes neuronales **por dentro**: su teoría y cómo programarlas desde conceptos simples. Esto es la base para después estudiar aprendizaje profundo (*deep learning*) y hacer cosas más complejas."

## Diapositiva 2 — Agenda (2 min)
Hoy vemos 4 temas, uno por cada video del curso:
1. Presentación.
2. Instalación de herramientas.
3. Inteligencia artificial y redes neuronales.
4. Aprendizaje automático.

## Diapositiva 3 — "Ya las usas todos los días" (10 min)
**Actividad (5 min):** pregunta "¿Qué aplicación con inteligencia artificial usaron hoy?". Anota las respuestas en el pizarrón.

**Explica cada tarjeta:**
- **Vehículos:** autos que ven la calle con cámaras y deciden cómo manejar.
- **Lenguaje:** Alexa, Google, traductores y chatbots entienden y producen texto.
- **Imagen:** los filtros de TikTok detectan tu cara y la modifican.
- **Salud:** detectan enfermedades en radiografías.
- **Videojuegos:** generan gráficos realistas más rápido. Calcular la luz real (*ray tracing*) es muy costoso.
- **Refuerzo:** programas que aprenden a jugar jugando muchas veces.
- **Generativa:** DALL·E y Stable Diffusion crean imágenes a partir de un texto. Hoy ya cuesta distinguir si una imagen la hizo una persona o una IA.
- **Robótica:** robots que perciben y se mueven.

**Mensaje clave:** las redes neuronales ya trabajan "por detrás" en muchos lados; por eso conviene saber cómo funcionan.

## Diapositiva 4 — "Dos formas de hacer los ejercicios" (5 min)
- Los ejercicios son **notebooks** con instrucciones: solo hay que **rellenar partes del código**.
- Usamos solo **Python y NumPy**, "a pie", a propósito. Así entendemos qué pasa por dentro, en lugar de llamar a una función mágica como `.fit()` que lo hace todo sin que veamos nada.
- **Opción 1, Colab:** no se configura nada; funciona en el navegador.
- **Opción 2, tu máquina:** más trabajo al inicio, pero es como se trabaja en proyectos reales y en equipo.

## Diapositiva 5 — "Instalación paso a paso" (25 min)
**Haz la instalación en vivo** siguiendo la **Parte A.3**, y que los alumnos la repitan.

Explica cada comando así:

| Comando | En palabras |
|---|---|
| `conda create --name nni python=3` | "Crea una caja llamada nni con Python 3 dentro." |
| `conda activate nni` | "Entra a la caja. Fíjense que ahora dice (nni)." |
| `pip install jupyter numpy ...` | "Mete en la caja las herramientas que vamos a usar." |
| `cd projects` | "Ve a mi carpeta de proyectos." |
| `git clone <url>` | "Descarga una copia del repositorio del curso." |
| `ls` | "Muéstrame qué archivos hay aquí." |
| VS Code → Abrir carpeta | "Abro el proyecto en el editor y elijo el kernel nni." |

Termina cuando todos vean la **Verificación final** del Paso 7. Quien no lo logre, que use Colab y lo resuelva después con la Parte C.

## Diapositiva 6 — "¿Qué es la inteligencia artificial?" (8 min)
- **No existe una definición única** aceptada por todos, ni un teorema que diga "esto sí es IA y esto no".
- El libro de **Russell y Norvig** (*Inteligencia Artificial: un enfoque moderno*) agrupa las definiciones en dos enfoques:
  1. **Imitar al humano:** construir máquinas que piensen como nosotros, duplicando lo que hace el cerebro. Problema: si copiamos perfectamente al humano, también copiamos sus errores.
  2. **Actuar racionalmente:** que la máquina **perciba** su entorno, **razone** (procese) y **actúe** para resolver el problema, aunque no lo haga como el cerebro.
- **Ejemplo:** una calculadora no piensa como humano, pero resuelve sumas perfectamente. Es "racional" para esa tarea.
- **Lectura:** capítulo 1 de Russell y Norvig.

## Diapositiva 7 — "El test de Turing" (10 min)
**El problema:** como no hay definición de inteligencia, Alan Turing propuso una **prueba**.

**Cómo funciona:**
1. Una persona conversa por mensajes, como en un chat, con "alguien" que no ve.
2. Del otro lado puede haber una persona o una máquina.
3. Si la persona **no logra distinguir** si habla con una máquina, la máquina **pasa** el test y se considera inteligente.

**¿Por qué es "operacional"?** Porque solo mide si pasa o no pasa; no le importa cómo funciona por dentro.

**Qué necesita una máquina para pasarlo** (explica cada tarjeta en orden, como un flujo):
1. **Lenguaje natural:** recibir y entender el mensaje.
2. **Representación del conocimiento:** convertir el mensaje en algo que la máquina pueda manejar internamente.
3. **Inferencia:** a partir de ese conocimiento, generar una respuesta.
4. **Síntesis:** convertir la respuesta otra vez en lenguaje para el humano.
5. **Aprendizaje:** adaptarse a cada usuario distinto.

**Conexión con el curso:** con el aprendizaje profundo, las redes neuronales ya cubren todas esas partes:
- extraen características a una representación interna llamada **espacio latente**;
- hacen inferencia;
- generan la salida con un **decodificador** (texto o imagen);
- y sus parámetros internos (**pesos**) se ajustan a cada tarea.

## Diapositiva 8 — "¿Qué tan lejos llegan las redes?" (8 min)
Dibuja **tres ejes** en el pizarrón:

| Eje | Significa | Redes neuronales |
|---|---|---|
| **Operacional** | Resolver la tarea: controlar, jugar, reconocer, generar | **Muy buenas**: reconocen personas, manejan autos, crean imágenes |
| **Razonamiento** | Representar conocimiento, inferir como humano y, al extremo, tener conciencia | Limitadas, al menos por ahora |
| **Explicabilidad** | Poder garantizar cuándo funcionan y cuándo no, y por qué | Limitadas: a veces fallan y no sabemos exactamente por qué |

**Conclusión:** son herramientas muy efectivas para resolver problemas, pero no tienen conciencia ni son completamente explicables. Por eso en el curso nos interesa mucho **cómo entrenarlas** bien.

## Diapositiva 9 — "Dónde encajan las redes neuronales" (5 min)
Dibuja **círculos uno dentro de otro**:
- **Inteligencia artificial** (el más grande): todo intento de que las máquinas hagan tareas inteligentes.
  - **Aprendizaje automático:** la parte de la IA que **aprende de ejemplos**.
    - **Redes neuronales:** un tipo de aprendizaje automático formado por muchas unidades simples conectadas.
      - **Aprendizaje profundo:** redes con **muchas capas**; cada capa extrae rasgos más abstractos (bordes → formas → objetos).

## Diapositiva 10 — "El aprendizaje automático" (8 min)
**Definición (Arthur Samuel, 1959):** "dar a las computadoras la capacidad de aprender sin ser programadas explícitamente".

**Ejemplo del ajedrez:**
- Queremos una computadora que gane al ajedrez.
- Un programador **no puede** escribir qué hacer en cada posición posible del tablero: hay muchísimas combinaciones, sería intratable.
- Solución: que la computadora **aprenda de la experiencia**, por ejemplo jugando muchas partidas.

**Definición en términos de aprendizaje:** un agente aprende si, **después de hacer observaciones (experiencia), mejora su desempeño** en futuras instancias de la tarea.

Tres ingredientes:
1. **Tarea:** ganar al ajedrez.
2. **Experiencia:** partidas jugadas o datos.
3. **Mejora del desempeño:** gana más seguido.

## Diapositiva 11 — "Tarea 1: Regresión" (10 min)
**Qué es:** encontrar una **función** que relacione una **entrada** con una **salida numérica continua**. Ejemplo: entrada = metros cuadrados de una casa; salida = precio.

**Explica la gráfica:**
- **Puntos naranjas = datos** (la "experiencia" o *dataset*). Pueden venir de estudios, mediciones o simulaciones.
- **Línea azul = la función real.** En la vida real **no la conocemos**; solo tenemos los puntos.
- **Líneas grises punteadas = hipótesis:** funciones candidatas que proponemos para explicar los puntos.

Conceptos:
- Una hipótesis es **consistente** si explica bien los datos que tenemos.
- Pero eso no basta: queremos que también funcione con **datos futuros** que vengan del mismo fenómeno. Eso se llama **generalización**.

**Pregunta a la clase:** "¿Una curva que pase exactamente por todos los puntos haciendo zigzag es buena?" → No necesariamente. Puede explicar estos datos y fallar con los nuevos.

## Diapositiva 12 — "Otras tareas" (10 min)
1. **Clasificación:** asignar una **etiqueta** de una lista predefinida {l₁, …, lₙ}. Ejemplo: le das una foto y responde "perro" o "gato" (dataset *Dogs vs Cats* de Kaggle). La diferencia con la regresión es que la salida es una **categoría**, no un número continuo.
2. **Agrupamiento (clustering):** **no hay etiquetas**. El algoritmo agrupa solo, por parecido. Ejemplo: con medidas como qué tan puntiagudas son las orejas o qué tan largos los bigotes, encuentra dos grupos (que resultan ser perros y gatos), cada uno con su **media** (centro) y su **varianza** (qué tan dispersos están).
3. **Reducción de dimensionalidad:** describir algo con **menos características**. Ejemplo: en 2 ejes, perros y gatos están revueltos y ninguna recta los separa. Si los proyectamos a 1 solo eje nuevo, basta un **umbral** (un punto) para separarlos. Simplifica el problema y ayuda a explicarlo.
4. **Modelado generativo:** aprender la **distribución** de los datos para **crear ejemplos nuevos**. Ejemplo: aprender "cómo es un rostro" y generar rostros que no existen. Se usa también para arte e imágenes.

## Diapositiva 13 — "Tipos de aprendizaje" (10 min)
1. **Supervisado:**
   - La experiencia es una lista de **pares (x, y)**: x = el ejemplo (una figura), y = su etiqueta (cono, cubo, esfera).
   - El algoritmo busca la función que lleva de x a y. Ese proceso se llama **entrenamiento**.
   - Luego debe acertar con ejemplos **nuevos** que nunca vio: **generalización**. Ejemplo: un auto autónomo debe manejar en calles donde nunca se entrenó.
2. **No supervisado:**
   - Hay ejemplos **sin etiquetas**.
   - El algoritmo descubre qué los distingue: los cubos tienen 6 caras; las esferas no tienen vértices aunque cambie su tamaño o color. Con eso los agrupa.
   - Un ejemplo nuevo cae en su grupo correspondiente.
3. **Por refuerzo:**
   - La experiencia **no está disponible** de antemano: se consigue **interactuando**.
   - Se detalla en la siguiente diapositiva.

## Diapositiva 14 — "Aprendizaje por refuerzo" (8 min)
Dibuja el ciclo **Agente ⇄ Ambiente**:
1. El **agente** (el programa) hace una **acción**, por ejemplo mover una pieza de ajedrez.
2. La acción cambia el **estado** del **ambiente** (el tablero).
3. El agente **observa** el nuevo estado y recibe una **recompensa**.
4. Se repite muchas veces.

Conceptos:
- **Recompensa a corto plazo:** comer una pieza.
- **Recompensa a largo plazo (horizonte):** ganar la partida. Es lo que realmente importa.
- **Objetivo:** maximizar la recompensa total.
- Al inicio el agente pierde mucho. Con la experiencia ajusta su regla de "en este estado, haz esta acción" y termina ganando.

**Cierre del tema:** las redes neuronales sirven para muchas de estas tareas: regresión, clasificación, reducción de dimensionalidad y generación. Algunas incluso aprenden su propia representación del conocimiento.

## Diapositiva 15 — Quiz (10 min)
Que respondan en papel durante 5 minutos y luego revisa en voz alta.

| # | Pregunta | Respuesta |
|---|---|---|
| 1 | ¿Por qué el test de Turing es una definición operacional? | Solo mide si pasa o no; no importa cómo funciona por dentro. |
| 2 | ¿En cuál de los tres ejes destacan las redes? | El operacional: resolver problemas. |
| 3 | ¿Qué es generalizar? | Funcionar bien con ejemplos que nunca vio. |
| 4 | ¿Diferencia entre clasificación y agrupamiento? | Clasificación tiene etiquetas predefinidas; agrupamiento no. |
| 5 | ¿Qué maximiza un agente de refuerzo? | La recompensa acumulada (a largo plazo). |

## Diapositiva 16 — "Para la próxima clase" (2 min)
1. Tener el ambiente instalado y el repositorio clonado (Parte A).
2. Leer **Russell y Norvig:** capítulo 1, y las secciones 18.1 y 18.2 (*Learning from examples*).
3. Leer **Goodfellow, Bengio y Courville, *Deep Learning*:** sección 5.1 (*Learning algorithms*).

La próxima clase empezaremos con la primera neurona artificial: el modelo de **McCulloch y Pitts**.

---

# PARTE C — Problemas frecuentes y soluciones

| Síntoma | Causa | Solución |
|---|---|---|
| `conda` no se reconoce como comando | Abriste PowerShell o CMD normal | Abre **Anaconda PowerShell Prompt** desde el menú Inicio |
| Sigue diciendo `(base)` | No activaste el ambiente | `conda activate nni` |
| `EnvironmentNameNotFound: nni` | El ambiente no se creó | Repite el Paso 2 y revisa con `conda env list` |
| `ModuleNotFoundError: No module named 'numpy'` en VS Code | El kernel elegido no es `nni` | Select Kernel → Python Environments → **nni** |
| VS Code no muestra `nni` en la lista de kernels | Falta `ipykernel` o la extensión | Con `(nni)` activo: `pip install ipykernel`; instala las extensiones Python y Jupyter; reinicia VS Code |
| `git` no se reconoce | Git no instalado o terminal abierta antes de instalarlo | Instala Git (Paso 5) y abre una **nueva** ventana de Git Bash |
| `destination path ... already exists` | Ya clonaste antes | No pasa nada; entra con `cd curso-redes-neuronales` |
| `ModuleNotFoundError: No module named 'nni'` | El notebook no se abrió desde la carpeta del repositorio | Abre en VS Code la carpeta `notebooks` completa, no el archivo suelto |
| `pip` falla con error de red o SSL | Internet o proxy de la institución | Prueba otra red, o usa Colab |
| La instalación de Anaconda falla por permisos | Sin permisos de administrador | Usa Colab (Camino 1) |
| Las tildes se ven como `�` en la terminal | Codificación de Windows | Ejecuta `chcp 65001` antes; es solo visual |
| Colab perdió mis cambios | No se guardó una copia | **Archivo → Guardar una copia en Drive** |

**Si nada funciona:** usa Colab en clase y revisa la instalación después, con calma, repitiendo la Parte A paso por paso.
