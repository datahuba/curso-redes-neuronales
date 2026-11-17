"""Genera los notebooks del proyecto «Reconocedor de dígitos» a partir de tools/proyecto_src/P*.py.

Formato de las fuentes (estilo «percent»):
    # %% [markdown]        -> celda de texto (se quita el «# » del inicio de cada línea)
    # %%                   -> celda de código
    #>> x = ...  # pista   -> en el notebook del alumno, todo hasta «#<<» se cambia por esta línea
    ...solución...
    #<<

Uso (desde la raíz del repo):
    python tools/build_proyecto.py           -> proyecto/P*.ipynb (alumno) y notebooks_resueltos/proyecto/ (docente)
    python tools/build_proyecto.py --probar  -> además ejecuta las soluciones de punta a punta
Las fuentes y los resueltos tienen las soluciones: están en .gitignore, nunca se publican.
"""
import glob
import os
import re
import shutil
import subprocess
import sys

import nbformat

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(RAIZ, "tools", "proyecto_src")
ALUMNO = os.path.join(RAIZ, "proyecto")
DOCENTE = os.path.join(RAIZ, "notebooks_resueltos", "proyecto")


def celdas(texto):
    """[(tipo, líneas)] de un archivo percent."""
    out = []
    for bloque in re.split(r"^# %%", texto, flags=re.M)[1:]:
        cab, _, cuerpo = bloque.partition("\n")
        out.append(("markdown" if "[markdown]" in cab else "code", cuerpo.rstrip("\n").split("\n")))
    return out


def version(lineas, alumno):
    out, saltar = [], False
    for ln in lineas:
        m = re.match(r"^(\s*)#>> ?(.*)$", ln)
        if m:
            saltar = True
            if alumno:
                out.append(m.group(1) + m.group(2))
        elif re.match(r"^\s*#<<", ln):
            saltar = False
        elif not (saltar and alumno):
            out.append(ln)
    return "\n".join(out).strip("\n")


def notebook(fuente, alumno):
    nb = nbformat.v4.new_notebook()
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    for tipo, lineas in celdas(open(fuente, encoding="utf-8").read()):
        if tipo == "markdown":
            nb.cells.append(nbformat.v4.new_markdown_cell(
                "\n".join(re.sub(r"^# ?", "", ln) for ln in lineas).strip("\n")))
        else:
            nb.cells.append(nbformat.v4.new_code_cell(version(lineas, alumno)))
    return nb


def probar(fuente):
    """Ejecuta la solución como script (gráficas sin ventana) dentro de proyecto/."""
    codigo = "\n\n".join(version(l, False) for t, l in celdas(open(fuente, encoding="utf-8").read()) if t == "code")
    env = dict(os.environ, MPLBACKEND="Agg", PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, "-c", codigo], cwd=ALUMNO, env=env, capture_output=True, text=True,
                       encoding="utf-8")
    print(r.stdout[-1500:])
    if r.returncode:
        print(r.stderr[-3000:])
        sys.exit(f"FALLÓ {os.path.basename(fuente)}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(DOCENTE, exist_ok=True)
    for f in ["digitos.py", "dibujar.py"]:          # para que los resueltos corran en su propia carpeta
        shutil.copy(os.path.join(ALUMNO, f), DOCENTE)
    solo = [a for a in sys.argv[1:] if not a.startswith("--")]      # ej.: build_proyecto.py --probar P5
    fuentes = [f for f in sorted(glob.glob(os.path.join(SRC, "P*.py")))
               if not solo or any(os.path.basename(f).startswith(s) for s in solo)]
    for f in fuentes:
        nombre = os.path.basename(f)[:-3] + ".ipynb"
        nbformat.write(notebook(f, True), os.path.join(ALUMNO, nombre))
        nbformat.write(notebook(f, False), os.path.join(DOCENTE, nombre))
        print("OK", nombre)
        if "--probar" in sys.argv:
            probar(f)
