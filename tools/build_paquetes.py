"""Arma los paquetes para repartir, a partir de entregables/ y proyecto/.

Uso (desde la raíz del repo, después de generar notebooks, diapositivas y PDF):
    python tools/build_paquetes.py --clase 1
Salida:
    PARA_ALUMNOS_Clase1/ y PARA_ALUMNOS_Clase1.zip   (solo esa clase: diapositivas + notebook, sin guías ni soluciones)
    MATERIAL_DOCENTE/ y MATERIAL_DOCENTE_curso_redes_neuronales.zip  (con soluciones: no publicar)
MATERIAL_DOCENTE/00_EMPIEZA_AQUI_Guia_del_docente.md se escribe a mano y se conserva.
"""
import glob
import os
import shutil
import sys

LEEME = """CURSO: INTRODUCCIÓN A LAS REDES NEURONALES · CLASE {n}
================================================

En este curso vas a construir desde cero, en Python, una red neuronal que
reconoce números escritos a mano. Cada clase agrega una pieza.

Clase_{n}_Presentacion.pdf  -> las diapositivas de hoy.
Proyecto/                   -> tu notebook de hoy: {nb}
{como}
Dentro del notebook, las celdas con ... son tuyas. Después de cada ejercicio,
una celda te dice si está bien (✅) o te da una pista (❌).

¿No puedes instalar Python? Usa Google Colab (solo necesitas cuenta de Google):
colab.research.google.com → Archivo → Abrir cuaderno → GitHub →
datahuba/curso-redes-neuronales → proyecto/{nb}
Para guardar tu trabajo: Archivo → Guardar una copia en Drive.

{lab}
Material basado en el curso del Dr. J. Irving Vasquez (jivg.org).
"""
LAB = "docs/lab/LABORATORIO_TEMA3.html"
LAB_NOMBRE = "LABORATORIO_INTERACTIVO.html"

COMO_1 = """
Cómo abrirlo (en tu computadora, con Python instalado en clase):
  1. Descomprime este zip (clic derecho → Extraer todo).
  2. En VS Code: File → Open Folder → elige la carpeta Proyecto (¡la carpeta completa!).
  3. Abre {nb}, elige el kernel nni (arriba a la derecha) y ejecuta las celdas con Shift + Enter.
"""
COMO_N = """
Cómo abrirlo:
  1. Descomprime este zip (clic derecho → Extraer todo).
  2. Copia {nb} a TU carpeta Proyecto (la de la Clase 1), junto a tus otros notebooks.
     (Si no la tienes, usa la carpeta Proyecto de este zip completa.)
  3. En VS Code: File → Open Folder → tu carpeta Proyecto → abre {nb} → kernel nni.
"""


def cp(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)


def proyecto(origen, destino):
    for f in glob.glob(origen + "/P*.ipynb") + [origen + "/digitos.py", origen + "/dibujar.py"]:
        cp(f, os.path.join(destino, os.path.basename(f)))
    cp("proyecto/datos/mnist.npz", os.path.join(destino, "datos", "mnist.npz"))   # para aulas sin internet
    cp("requirements.txt", os.path.join(destino, "requirements.txt"))


def apoyo(destino):
    shutil.copytree("notebooks", destino, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("output", "__pycache__", ".ipynb_checkpoints"))
    cp("entregables/Guias_de_los_notebooks.pdf", os.path.join(destino, "Guias_de_los_notebooks.pdf"))


def alumnos(n, con_lab=False):
    """Paquete de UNA clase para los alumnos: sus diapositivas y su notebook (sin guías ni soluciones)."""
    A = f"PARA_ALUMNOS_Clase{n}"
    shutil.rmtree(A, ignore_errors=True)
    cp(f"entregables/Clase{n}_Diapositivas.pdf", f"{A}/Clase_{n}_Presentacion.pdf")
    nb = os.path.basename(glob.glob(f"proyecto/P{n}_*.ipynb")[0])
    for f in [nb, "digitos.py"] + (["dibujar.py"] if n >= 4 else []):
        cp(os.path.join("proyecto", f), f"{A}/Proyecto/{f}")
    cp("proyecto/datos/mnist.npz", f"{A}/Proyecto/datos/mnist.npz")       # para aulas sin internet
    cp("requirements.txt", f"{A}/Proyecto/requirements.txt")
    texto_lab = ""
    if con_lab and os.path.exists(LAB):
        cp(LAB, f"{A}/{LAB_NOMBRE}")
        texto_lab = (f"{LAB_NOMBRE}   -> el laboratorio de hoy: una pagina web con los ejercicios,\n"
                     "  los simuladores y los datos. Abrela con doble clic: no necesita internet\n"
                     "  ni instalar nada. Se trabaja en equipos de 3.\n")
    como = (COMO_1 if n == 1 else COMO_N).format(nb=nb)
    open(f"{A}/LEEME.txt", "w", encoding="utf-8").write(LEEME.format(n=n, nb=nb, como=como, lab=texto_lab))
    t = open(f"{A}/Proyecto/{nb}", encoding="utf-8").read()                # nunca soluciones
    assert "X[y_train == d].mean(axis=0)" not in t and "dA1 = dZ2 @" not in t and "beta * v - eta" not in t, nb
    shutil.make_archive(A, "zip", ".", A)
    return A + ".zip"


def docente(D="MATERIAL_DOCENTE"):
    for sub in ["1_Guias_de_clase", "2_Diapositivas", "3_Proyecto_alumno", "4_Proyecto_resuelto", "6_Apoyo_opcional"]:
        shutil.rmtree(os.path.join(D, sub), ignore_errors=True)
    for n in range(1, 8):
        cp(f"entregables/Clase{n}_Guia.pdf", f"{D}/1_Guias_de_clase/Clase_{n}_Guia.pdf")
        for ext in ["pptx", "pdf"]:
            cp(f"entregables/Clase{n}_Diapositivas.{ext}", f"{D}/2_Diapositivas/Clase_{n}_Diapositivas.{ext}")
    proyecto("proyecto", f"{D}/3_Proyecto_alumno")
    proyecto("notebooks_resueltos/proyecto", f"{D}/4_Proyecto_resuelto")
    cp("entregables/Curso_Completo.pdf", f"{D}/5_Curso_completo.pdf")
    apoyo(f"{D}/6_Apoyo_opcional")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    clase = int(sys.argv[sys.argv.index("--clase") + 1]) if "--clase" in sys.argv else 1
    z_alumnos = alumnos(clase, con_lab="--lab" in sys.argv)
    docente()
    cp(z_alumnos, f"MATERIAL_DOCENTE/{z_alumnos}")
    shutil.make_archive("MATERIAL_DOCENTE_curso_redes_neuronales", "zip", ".", "MATERIAL_DOCENTE")
    for z in [z_alumnos, "MATERIAL_DOCENTE_curso_redes_neuronales.zip"]:
        print(z, f"{os.path.getsize(z) / 1e6:.1f} MB")
