"""Arma los paquetes para repartir, a partir de entregables/ y proyecto/.

Uso (desde la raíz del repo, después de generar notebooks, diapositivas y PDF):
    python tools/build_paquetes.py
Salida:
    PARA_ALUMNOS/ y PARA_ALUMNOS_curso_redes_neuronales.zip          (sin soluciones)
    MATERIAL_DOCENTE/ y MATERIAL_DOCENTE_curso_redes_neuronales.zip  (con soluciones: no publicar)
MATERIAL_DOCENTE/00_EMPIEZA_AQUI_Guia_del_docente.md se escribe a mano y se conserva.
"""
import glob
import os
import shutil
import sys

LEEME = """CURSO: INTRODUCCIÓN A LAS REDES NEURONALES
==========================================

En este curso vas a construir desde cero, en Python, una red neuronal que
reconoce números escritos a mano. Cada clase agrega una pieza.

1_Guias            -> una guía por clase (Clase_1 a Clase_7).
2_Presentaciones   -> las diapositivas de cada clase.
3_Proyecto         -> TU PROYECTO: un notebook por clase (P1 a P7).
                      IMPORTANTE: abre la carpeta 3_Proyecto COMPLETA en VS Code.
                      No saques los notebooks de ahí: necesitan digitos.py y la carpeta datos/.
                      Las celdas con ... son tuyas; después de cada ejercicio una celda
                      te dice si está bien (✅) o te da una pista (❌).
                      Desde la Clase 4:  python dibujar.py  -> dibuja un número y tu red lo adivina.
4_Apoyo_opcional   -> ejercicios extra para reforzar (no son obligatorios).

Cómo instalar todo: 1_Guias/Clase_1_Guia.pdf, Parte A.
Para instalar los paquetes, dentro de 3_Proyecto:   pip install -r requirements.txt

Clase 1: P1  ·  Clase 2: P2  ·  Clase 3: P3  ·  Clase 4: P4  ·  Clase 5: P5  ·  Clase 6: P6  ·  Clase 7: P7

Material basado en el curso del Dr. J. Irving Vasquez (jivg.org).
Repositorio: https://github.com/datahuba/curso-redes-neuronales
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


def alumnos(A="PARA_ALUMNOS"):
    shutil.rmtree(A, ignore_errors=True)
    for n in range(1, 8):
        cp(f"entregables/Clase{n}_Guia.pdf", f"{A}/1_Guias/Clase_{n}_Guia.pdf")
        cp(f"entregables/Clase{n}_Diapositivas.pdf", f"{A}/2_Presentaciones/Clase_{n}_Presentacion.pdf")
    proyecto("proyecto", f"{A}/3_Proyecto")
    apoyo(f"{A}/4_Apoyo_opcional")
    open(f"{A}/LEEME.txt", "w", encoding="utf-8").write(LEEME)
    # nunca soluciones en el paquete de alumnos
    for f in glob.glob(A + "/3_Proyecto/*.ipynb"):
        t = open(f, encoding="utf-8").read()
        assert "X[y_train == d].mean(axis=0)" not in t and "dA1 = dZ2 @" not in t, f"¡solución en {f}!"


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
    alumnos()
    shutil.make_archive("PARA_ALUMNOS_curso_redes_neuronales", "zip", ".", "PARA_ALUMNOS")
    docente()
    cp("PARA_ALUMNOS_curso_redes_neuronales.zip", "MATERIAL_DOCENTE/PARA_ALUMNOS.zip")
    shutil.make_archive("MATERIAL_DOCENTE_curso_redes_neuronales", "zip", ".", "MATERIAL_DOCENTE")
    for z in ["PARA_ALUMNOS_curso_redes_neuronales.zip", "MATERIAL_DOCENTE_curso_redes_neuronales.zip"]:
        print(z, f"{os.path.getsize(z) / 1e6:.1f} MB")
