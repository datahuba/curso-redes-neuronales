# Guía paso a paso — Clase 1: El proyecto y los datos

**El proyecto del curso:** construir desde cero, en Python y NumPy, una red neuronal que **reconoce números escritos a mano**. En la última clase cada alumno dibuja un número con el mouse y su propia red lo adivina.
**Pieza de hoy:** instalar todo, conocer los 70 000 dígitos de MNIST y armar una primera «IA» que acierta el 82 % sin una sola neurona.
**Duración:** ~2 h de clase, más 15–30 min de margen para dudas
**Material:** diapositivas `Clase1_Diapositivas` · notebook `proyecto/P1_conocer_los_datos.ipynb` · repositorio https://github.com/datahuba/curso-redes-neuronales

**Cómo es el curso desde ahora:** directo a la práctica. Cada clase arranca con el notebook abierto y la teoría entra en pausas cortas, justo cuando el ejercicio la necesita. Cada clase termina con algo que corre y una precisión medida.

La guía tiene tres partes:
- **Parte A:** preparar las computadoras **antes** de clase (instalación rigurosa, con verificación en cada paso).
- **Parte B:** la clase paso a paso: pasos de práctica y pausas cortas de teoría.
- **Parte C:** problemas frecuentes.

## Objetivos de la clase

Al terminar, cada alumno podrá:
1. Explicar qué vamos a construir en el curso y en qué se diferencia «programar reglas» de «aprender de datos».
2. Cargar MNIST, ver que una imagen es una tabla de números y prepararla (aplanar y normalizar).
3. Construir un clasificador por plantillas y medir su **precisión** con datos de prueba.

## Agenda

> **Cómo se da esta clase:** directo a la práctica. Los alumnos abren el notebook en el minuto 2 y la teoría entra en **pausas cortas** (⏸) justo cuando el ejercicio la necesita. Regla de oro: **primero lo hacen, después lo explicas** (o, si hace falta para poder hacerlo, lo explicas en 3–5 minutos y vuelven al teclado). Las diapositivas siguen el mismo orden: «Paso» (oscuras) = trabajan; «Pausa · teoría» (claras) = explicas.

| Tiempo | Qué pasa |
|---|---|
| 0:00 | Demo: dibujan un número y la red lo adivina (2 min) |
| 0:02 | **Paso 1** · Instalar (40 min) |
| 0:42 | **Paso 2** · Abrir el proyecto `P1` (5 min) |
| 0:47 | **Paso 3** · Mirar los datos (15 min) |
| 1:02 | ⏸ Pausa: una imagen es una tabla de números (3 min) |
| 1:05 | **Paso 4** · Preparar los datos (10 min) |
| 1:15 | Descanso (10 min) |
| 1:25 | ⏸ Pausa: reglas vs ejemplos, plantillas (3 min) |
| 1:28 | **Paso 5** · La IA de plantillas y el examen (30 min) |
| 1:58 | Resultado (82 %), mapa del proyecto y cierre (15 min) |

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
| **Terminal** | Ventana donde se escriben comandos de texto. Usaremos **Anaconda PowerShell Prompt**. |
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

1. Entra a https://colab.research.google.com e inicia sesión con tu cuenta de Google.
2. Menú **Archivo → Abrir cuaderno** → pestaña **GitHub**.
3. Pega `datahuba/curso-redes-neuronales` y presiona Enter.
4. Elige el notebook, por ejemplo `proyecto/P1_conocer_los_datos.ipynb`.
5. Haz clic en la primera celda de código y presiona **Shift + Enter** para ejecutarla.
6. Para guardar tus cambios: **Archivo → Guardar una copia en Drive**. Si no lo haces, se pierden.

**Verificación:** crea una celda nueva (botón **+ Código**), escribe esto y ejecútala:

```python
import numpy as np
print(np.__version__)
```

Si aparece un número de versión (por ejemplo `1.26.4`), Colab funciona.

**Los notebooks del proyecto** (`proyecto/P1` … `P7`) funcionan en Colab tal cual: su primera celda descarga sola las herramientas (`digitos.py`) y los datos.

**Los notebooks de apoyo** de la carpeta `notebooks/` que usan la carpeta `nni` o archivos de datos (como `1_03_2`) necesitan el repositorio completo. Ejecuta esto en la primera celda:

```python
!git clone https://github.com/datahuba/curso-redes-neuronales
%cd curso-redes-neuronales/notebooks
```

---

## A.3 Camino 2 — Instalación local en Windows

Son **7 pasos**, en este orden:
- Pasos 1 a 3: instalar tres programas, con clics.
- Pasos 4 a 7: escribir comandos en **una sola** terminal, Anaconda PowerShell Prompt.

### Paso 1. Instalar Anaconda

1. Entra a https://www.anaconda.com/download
2. Descarga el instalador para **Windows** (64 bits).
3. Ejecuta el archivo descargado (`Anaconda3-...-Windows-x86_64.exe`).
4. En el instalador:
   - **Next → I Agree**.
   - Elige **Just Me (recommended)**.
   - Deja la carpeta que propone. Es importante que la ruta no tenga espacios ni acentos; normalmente es `C:\Users\TuUsuario\anaconda3`.
   - En opciones avanzadas, deja marcadas las que vienen por defecto. **No** marques "Add Anaconda to my PATH".
   - **Install** y espera de 5 a 15 minutos → **Finish**.

**Verificación:**
1. Abre el menú Inicio, escribe `Anaconda PowerShell Prompt` y ábrelo.
2. Debe verse una línea que empieza con `(base)`, por ejemplo:
   ```
   (base) PS C:\Users\TuUsuario>
   ```
3. Escribe y presiona Enter:
   ```bash
   conda --version
   ```
   Debe responder algo como `conda 24.x.x`.

> Anaconda tiene una interfaz gráfica (Anaconda Navigator), pero es lenta. Usaremos la terminal.

### Paso 2. Instalar Git for Windows

1. Entra a https://git-scm.com/download/win
2. Descarga **64-bit Git for Windows Setup** y ejecútalo.
3. Acepta todas las opciones por defecto (**Next** en todo) → **Install** → **Finish**.

**Verificación:** **cierra y vuelve a abrir** Anaconda PowerShell Prompt (así reconoce el programa nuevo) y escribe:

```bash
git --version
```

Debe responder algo como `git version 2.4x.x.windows.1`.

### Paso 3. Instalar VS Code y sus extensiones

1. Entra a https://code.visualstudio.com, descarga e instala con las opciones por defecto. Marca **"Agregar a PATH"** si aparece.
2. Abre VS Code.
3. Instala dos extensiones:
   1. Haz clic en el ícono de **Extensiones** de la barra izquierda (cuatro cuadritos) o presiona `Ctrl + Shift + X`.
   2. Busca **Python** (de Microsoft) → **Install**.
   3. Busca **Jupyter** (de Microsoft) → **Install**.

**Verificación:** en la barra izquierda, dentro de Extensiones, aparecen **Python** y **Jupyter** como instaladas.

### Paso 4. Crear y activar el ambiente `nni`

En **Anaconda PowerShell Prompt** escribe:

```bash
conda create --name nni python=3.11
```

Qué significa:
- `conda create` → crea un ambiente nuevo.
- `--name nni` → le pone de nombre `nni`.
- `python=3.11` → le instala Python 3.11. En el video se usa `python=3`; 3.11 es una versión 3 concreta y estable.

Cuando pregunte `Proceed ([y]/n)?`, escribe `y` y presiona Enter. Tarda de 1 a 3 minutos.

Luego actívalo:

```bash
conda activate nni
```

**Verificación:** el inicio de la línea debe cambiar de `(base)` a `(nni)`:
```
(nni) PS C:\Users\TuUsuario>
```

⚠️ **Cada vez que abras una terminal nueva**, el ambiente vuelve a `(base)`. Debes repetir `conda activate nni`.

### Paso 5. Descargar (clonar) el repositorio del curso

En la misma terminal, con `(nni)` visible:

```bash
cd ~
```
```bash
mkdir projects
```
```bash
cd projects
```
```bash
git clone https://github.com/datahuba/curso-redes-neuronales.git
```
```bash
cd curso-redes-neuronales
```

Qué significa:
- `cd ~` → ir a tu carpeta de usuario.
- `mkdir projects` → crear una carpeta `projects`. Si ya existía, muestra un error en rojo; no pasa nada, continúa.
- `cd projects` → entrar a esa carpeta.
- `git clone <url>` → descargar una copia del repositorio.
- `cd curso-redes-neuronales` → entrar a la carpeta del curso.

**Verificación:** escribe `ls`. Deben aparecer `docs`, `notebooks`, `README.md` y `requirements.txt`.

> **Alternativa sin Git:** en GitHub, botón verde **Code → Download ZIP**. Descomprímelo en `C:\Users\TuUsuario\projects` y entra a esa carpeta con `cd`.
>
> En el video se usa la terminal **Git Bash** para clonar; también funciona, pero así usamos una sola ventana para todo.

### Paso 6. Instalar los paquetes

Dentro de la carpeta `curso-redes-neuronales`, con `(nni)` activo:

```bash
pip install -r requirements.txt
```

`-r requirements.txt` le dice a pip que instale **la lista de paquetes del curso**, que viene en ese archivo:

| Paquete | Para qué |
|---|---|
| `jupyter` | Ejecutar notebooks |
| `numpy` | Vectores, matrices y cuentas |
| `pandas` | Tablas de datos |
| `matplotlib` | Gráficas |
| `scikit-learn` | Utilidades de aprendizaje automático (el notebook `1_03_2` lo necesita) |
| `pillow` | Abrir imágenes |
| `ipykernel` | Que VS Code reconozca el ambiente como kernel |

Tarda de 2 a 5 minutos. La última línea debe decir `Successfully installed ...`.

**Verificación:**

```bash
python -c "import numpy, pandas, matplotlib, sklearn, PIL; print('TODO OK')"
```

Debe imprimir `TODO OK`. Si dice `ModuleNotFoundError`, revisa que estés en `(nni)` y repite el Paso 6.

### Paso 7. Abrir los notebooks en VS Code (verificación final)

1. En VS Code: **File → Open Folder…** (Archivo → Abrir carpeta) → elige `C:\Users\TuUsuario\projects\curso-redes-neuronales` → **Seleccionar carpeta**. Si pregunta si confías en los autores, elige **Yes, I trust**.
2. En el panel izquierdo abre `proyecto` → `P1_conocer_los_datos.ipynb`.
3. **Elige el kernel (muy importante):**
   1. Arriba a la derecha, haz clic en **Select Kernel**.
   2. Elige **Python Environments…**.
   3. Elige el que diga **nni**, por ejemplo `nni (Python 3.11.x)`.
4. Crea una celda (botón **+ Code**), escribe esto y ejecútalo con **Shift + Enter**:

```python
import sys, numpy as np
print(sys.executable)
print(np.__version__)
```

**Verificación final:**
- La primera línea debe contener `envs\nni`; eso prueba que usas el ambiente correcto.
- La segunda debe ser un número de versión.

✅ Si ves ambas cosas, **la computadora está lista**. Borra la celda de prueba.

### Resumen de comandos (para copiar)

Todo en **Anaconda PowerShell Prompt**:

```bash
conda create --name nni python=3.11
```
```bash
conda activate nni
```
```bash
cd ~
```
```bash
mkdir projects
```
```bash
cd projects
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

**Alternativa sin VS Code:** con `(nni)` activo, dentro de `curso-redes-neuronales`:

```bash
jupyter notebook
```

Se abre el navegador con la lista de archivos. Para cerrarlo, en la terminal presiona `Ctrl + C`.

---

## A.4 Checklist del día de la clase

- [ ] Tu computadora pasó la **verificación final** del Paso 7.
- [ ] Probaste abrir un notebook en **Colab** (plan B).
- [ ] Tienes abiertas las diapositivas.
- [ ] Preparaste la demo de `dibujar.py` (A.5).
- [ ] Llegaste 15 minutos antes para probar el proyector.
- [ ] Si los alumnos instalarán en clase, avísales que traigan laptop con **5 GB libres** y permisos de administrador. Si pueden, que descarguen Anaconda en casa: son unos 900 MB.


## A.5 Preparar la demo (docente, 10 min)

La clase empieza mostrando el **final** del curso. Hazlo la noche anterior:

1. `python tools/build_proyecto.py` (solo en tu computadora: genera los notebooks resueltos en `notebooks_resueltos/proyecto/`).
2. Abre `notebooks_resueltos/proyecto/P5_red_multicapa.ipynb` y ejecútalo entero (~1 min). Al final guarda `pesos.npz`.
3. En una terminal, dentro de `notebooks_resueltos/proyecto/`: `python dibujar.py`. Dibuja un 3, un 7, un 0. Deja la ventana lista.

> Si `tools/build_proyecto.py` dice que no encuentra `tools/proyecto_src`, te falta la carpeta con las fuentes (no está en GitHub porque tiene las soluciones). Cópiala desde tu computadora de trabajo.

---

# PARTE B — La clase paso a paso

## Demo (2 min)
Abre `dibujar.py` en el proyector y **pide a un alumno que dibuje un número**. La red lo adivina. Di solo: *«Esto lo van a programar ustedes, en 7 clases. Empezamos ya.»* Nada de teoría todavía.

## Paso 1 · Instalar (40 min)
Sigue la **Parte A** (Colab o instalación local). Quien termina primero ayuda a su compañero; quien se trabe más de 10 min sigue en **Colab** y lo arreglan después.

## Paso 2 · Abrir el proyecto (5 min)
**Haz:** abrir `proyecto/P1_conocer_los_datos.ipynb`, elegir el kernel **nni**, ejecutar las dos primeras celdas (Shift + Enter).
**Deben ver:** `X_train: (60000, 28, 28)`. Quien lo ve, terminó de instalar.
Explica en 30 segundos la dinámica: las celdas con `...` son suyas; después de cada ejercicio hay una comprobación ✅/❌ con pista.

## Paso 3 · Mirar los datos (15 min)
**Haz:** ejecutar `mostrar(...)` y la celda que imprime la tabla de números; **Ejercicio 1** (`np.bincount`).
**Deben ver:** ~6 000 ejemplos de cada dígito.
**Reto mientras tanto:** *¿encuentras el 5 dentro de la tabla de números?*

## ⏸ Pausa: una imagen es una tabla de números (3 min)
**Cuándo:** cuando la mayoría vio la tabla.
**Di:** cada imagen son 28 × 28 = 784 números, 0 negro y 255 blanco. Para la red será **una fila de 784 números entre 0 y 1**. Y hay 60 000 imágenes para aprender y 10 000 para el examen: *si el examen trae las preguntas de la práctica, no sabes si el alumno entendió o memorizó*.

## Paso 4 · Preparar los datos (10 min)
**Haz:** Ejercicio 2: `reshape(60000, 784) / 255` (y lo mismo para la prueba).
**Error típico:** `reshape(784)` sin decir cuántas imágenes son. La comprobación lo detecta.

## Descanso (10 min)

## ⏸ Pausa: reglas vs ejemplos (3 min)
**Pregunta primero:** *¿cómo le explicarías a una computadora qué es un 7?* Deja que propongan reglas y muestra cómo fallan (7 con rayita, inclinado…).
**Di:** en vez de reglas, **aprender de ejemplos**. Idea de hoy: promediar los 6 000 «tres» → el tres típico (plantilla). Muestra las plantillas en la diapositiva.

## Paso 5 · La IA de plantillas (30 min)
**Haz:** Ejercicio 3 (`X[y_train == d].mean(axis=0)`), Ejercicio 4 (`predecir`: la plantilla más parecida con `argmin`), y el examen.
**Deben ver:** `Precisión: 82.0%`.
**Si se traban:** explica la máscara `y_train == d` (lista de Verdadero/Falso que filtra filas).
**Al final:** miren juntos los errores. *¿Tú también los confundirías?*

## Resultado y cierre (15 min)
- Diapositiva **82 %**: al azar sería 10 %; pero 1 de cada 5 mal es mucho. Y **las plantillas nunca cambian**: no aprenden de sus errores.
- **Mapa del proyecto:** así avanzará el curso.
- **Tarea:** terminar `P1`. Desafío: ¿y si usas el producto punto (`plantillas @ x`) con `argmax`?
- **Próxima clase:** una neurona que corrige sus pesos cuando se equivoca.

---

# PARTE C — Problemas frecuentes y soluciones

| Síntoma | Causa | Solución |
|---|---|---|
| `conda` no se reconoce como comando | Abriste PowerShell o CMD normal | Abre **Anaconda PowerShell Prompt** desde el menú Inicio |
| Sigue diciendo `(base)` | No activaste el ambiente | `conda activate nni` |
| `EnvironmentNameNotFound: nni` | El ambiente no se creó | Repite el Paso 4 y revisa con `conda env list` |
| `git` no se reconoce | Git no instalado, o terminal abierta antes de instalarlo | Instala Git (Paso 2) y **abre una terminal nueva** |
| `mkdir` dice que la carpeta ya existe | Ya la habías creado | No es un error grave; sigue con `cd projects` |
| `destination path ... already exists` | Ya clonaste antes | No pasa nada; entra con `cd curso-redes-neuronales` y actualiza con `git pull` |
| `Could not open requirements file` | No estás dentro de `curso-redes-neuronales` | `cd ~\projects\curso-redes-neuronales` y repite el Paso 6 |
| `ModuleNotFoundError: No module named 'numpy'` en VS Code | El kernel elegido no es `nni` | Select Kernel → Python Environments → **nni** |
| VS Code no muestra `nni` en la lista de kernels | Falta `ipykernel` o la extensión | Con `(nni)` activo: `pip install ipykernel`; instala las extensiones Python y Jupyter; reinicia VS Code |
| `ModuleNotFoundError: No module named 'nni'` | El notebook no se abrió desde el repositorio | Abre en VS Code la carpeta `curso-redes-neuronales` completa, no el archivo suelto |
| `pip` falla con error de red o SSL | Internet o proxy de la institución | Prueba otra red, o usa Colab |
| La instalación de Anaconda falla por permisos | Sin permisos de administrador | Usa Colab (Camino 1) |
| Las tildes se ven como `�` en la terminal | Codificación de Windows | Ejecuta `chcp 65001` antes; es solo visual |
| `ModuleNotFoundError: No module named 'digitos'` | El notebook no se abrió desde la carpeta `proyecto/` | Abre en VS Code la carpeta `curso-redes-neuronales` completa y el notebook desde `proyecto/`; en Colab la primera celda lo descarga sola |
| La descarga de MNIST falla | Sin internet o proxy | Copia `proyecto/datos/mnist.npz` desde otra computadora (con USB) |
| `NameError` en una celda | Se saltaron una celda anterior | **Run All** (Ejecutar todo) desde arriba |
| Colab perdió mis cambios | No se guardó una copia | **Archivo → Guardar una copia en Drive** |

**Si nada funciona:** usa Colab en clase y revisa la instalación después, con calma, repitiendo la Parte A paso por paso.
