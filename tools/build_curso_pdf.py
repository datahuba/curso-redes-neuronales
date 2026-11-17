"""Une todo el curso en un solo PDF: portada e índice, y por cada clase su guía, sus diapositivas y las guías
de sus notebooks. Agrega marcadores (índice lateral del lector de PDF).

Uso (desde la raíz del repo, después de generar los PDF de entregables/):
    python tools/build_curso_pdf.py
Salida: entregables/Curso_Completo.pdf
"""
import os
import subprocess
import sys
import tempfile

import pymupdf

E = "entregables"
CLASES = [   # (n, tema, guías de notebooks de apoyo): el proyecto se trabaja en proyecto/P1..P7
    (1, "El proyecto y los datos", []),
    (2, "Una neurona que aprende de sus errores", []),
    (3, "Aprender bajando la montaña (descenso por gradiente)", []),
    (4, "Diez neuronas: reconocer del 0 al 9", []),
    (5, "La red de verdad: capa oculta y retropropagación", []),
    (6, "Entrenar más rápido y mejor (optimizadores)", []),
    (7, "Redes convolucionales y cierre del proyecto", []),
]


def partes():
    """Lista ordenada de (nivel, título, archivo pdf)."""
    out = []
    for n, tema, nbs in CLASES:
        out.append((1, f"Clase {n} · {tema}", None))
        out.append((2, "Guía de la clase", f"{E}/Clase{n}_Guia.pdf"))
        out.append((2, "Diapositivas", f"{E}/Clase{n}_Diapositivas.pdf"))
        for nb in nbs:
            out.append((2, f"Guía del notebook {nb}", f"{E}/guias_notebooks/NB_{nb}.pdf"))
    return out


def indice_md(paginas):
    lineas = ["# Introducción a las Redes Neuronales — Curso completo", "",
              "**Repositorio:** https://github.com/datahuba/curso-redes-neuronales  ",
              "**Basado en** el curso, el libro y los notebooks del Dr. J. Irving Vasquez (jivg.org).", "",
              "Este documento reúne, en orden, las 7 clases. Cada clase incluye:",
              "- su **guía paso a paso**;",
              "- sus **diapositivas**.", "",
              "El curso es un solo proyecto: construir desde cero un **reconocedor de dígitos escritos a mano**. "
              "Cada clase agrega una pieza en su notebook (`proyecto/P1` … `P7`), que se trabaja en la computadora.", "",
              "## Contenido", "", "| Sección | Página |", "|---|---|"]
    for (nivel, titulo, _), pag in zip(partes(), paginas):
        if nivel == 1:
            lineas.append(f"| **{titulo}** | **{pag}** |")
        else:
            lineas.append(f"| &nbsp;&nbsp;&nbsp;&nbsp;{titulo} | {pag} |")
    return "\n".join(lineas).replace("&nbsp;", " ")


def render_indice(paginas, tmp):
    md = os.path.join(tmp, "indice.md")
    pdf = os.path.join(tmp, "indice.pdf")
    open(md, "w", encoding="utf-8").write(indice_md(paginas))
    subprocess.run([sys.executable, "-X", "utf8", "tools/md_to_pdf.py", md, pdf], check=True, capture_output=True)
    return pdf


def main():
    ps = partes()
    faltan = [f for _, _, f in ps if f and not os.path.exists(f)]
    if faltan:
        sys.exit(f"Faltan PDF: {faltan}")
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        n_indice = 1
        for _ in range(3):                      # el índice puede ocupar varias páginas: se ajusta
            paginas, pag = [], n_indice + 1
            for _, _, f in ps:
                paginas.append(pag)
                if f:
                    pag += pymupdf.open(f).page_count
            ind = render_indice(paginas, tmp)
            real = pymupdf.open(ind).page_count
            if real == n_indice:
                break
            n_indice = real
        doc = pymupdf.open(ind)
        toc = [[1, "Contenido", 1]]
        for (nivel, titulo, f), p in zip(ps, paginas):
            toc.append([nivel, titulo, p])
            if f:
                doc.insert_pdf(pymupdf.open(f))
        doc.set_toc(toc)
        out = os.path.join(E, "Curso_Completo.pdf")
        doc.save(out, garbage=3, deflate=True)
        total = doc.page_count
        doc.close()
        print(out, total, "páginas,", round(os.path.getsize(out) / 1e6, 1), "MB")


if __name__ == "__main__":
    main()
