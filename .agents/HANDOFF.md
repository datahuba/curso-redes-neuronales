# HANDOFF

## Sesión: Curso de Redes Neuronales — clase 1, repo y diapositivas (2026-10-14)

**Objetivo:** armar el curso "Introducción a las Redes Neuronales" basado en el material del Dr. J. Irving Vasquez (jivg.org): guías, prácticas, notebooks y diapositivas para dar la clase 1.

**Estado actual**
- Repo PÚBLICO: https://github.com/datahuba/curso-redes-neuronales (rama `main`, ya pusheado).
  - `README.md`, `requirements.txt`.
  - `docs/` (GUIA_PASO_A_PASO_CLASE1.md, CURSO.md, 01_Introduccion.md, 02_Principios.md, practica_02.py).
  - `notebooks/` (17 notebooks de irvingvasquez/cv2course_intro_nn, CC BY 4.0, sin soluciones).
- Diapositivas (Artifact privado, 16 slides, clase 1 = los 4 primeros videos: presentación, instalación, IA y redes, aprendizaje automático): https://claude.ai/artifact/9vRb7zDTg2JWdN1B1YQL4j. Las diapositivas de instalación ya apuntan a `datahuba/curso-redes-neuronales`.
- Solo local (en `.gitignore`, NO publicar):
  - `soluciones_docente_m1_m2.py` (clave del docente, verificada con asserts).
  - `GUIA_CLASE_M1_M2.md` (guía docente de módulos 1 y 2, con soluciones).
  - `material/` (clon del repo original y copia HTML del libro, que es CC BY-NC).

**Decisiones**
- Las soluciones nunca van al repo público.
- El libro se enlaza, no se redistribuye.
- Se usa `python=3.11` en lugar de `python=3`; se agregaron `scikit-learn` e `ipykernel` a los requisitos.

**Intentos fallidos / notas**
- `read_terminal` no mostró el comando que corrió el usuario: el panel estaba vacío.
- `notebooks/1_01_mcculloch_pitts.ipynb` aparece modificado localmente, no por esta sesión (probablemente el usuario lo ejecutó). No se commiteó.

**Próximos pasos**
1. Guía paso a paso: decidir si instala paquetes después de clonar (`pip install -r requirements.txt`), igual que la diapositiva.
2. Clase 2: módulo 2 (McCulloch-Pitts y perceptrón). Las notas ya están en `docs/02_Principios.md`; faltan las diapositivas.
3. Módulo 3: red neuronal simple y descenso por gradiente (notebooks 1_04 a 1_08).

**Pendiente de Kevin**
- Compartir las diapositivas (menú Compartir) si los alumnos deben verlas.
- Elegir licencia para el contenido propio del repo.
- ¿Recortar `GUIA_CLASE_M1_M2.md` a los 4 temas de la clase 1?

## Actualización (2026-11-02): PDFs, PowerPoint y plan de la clase 3
- `entregables/`: Clase1/Clase2 _Guia.pdf, _Diapositivas.pptx y .pdf (19 y 21 diapositivas). Se regeneran con
  `python tools/build_decks.py` + `powershell -File tools/export_pdf.ps1` (usa PowerPoint) y
  `python tools/md_to_pdf.py <md> <pdf>` (markdown-it + Chrome; fórmulas con KaTeX).
- Guía clase 1 reordenada: instalar programas (Anaconda, Git, VS Code) y luego todo en Anaconda PowerShell
  (conda → git clone → `pip install -r requirements.txt`). Las diapositivas siguen ese mismo orden.
- `docs/PLAN_CLASE3.md`: propuesta de partir el módulo 3 en clases 3 y 4. El libro tiene un error de cuentas en el
  ejemplo de varias salidas (H correcto = [−4.7, 6.3]).
- Nada de esto está commiteado ni pusheado: pendiente de confirmación de Kevin.

## Actualización (2026-11-02, tarde): clases 3 y 4
- Módulo 3 dividido en Clase 3 (neurona moderna, activaciones, derivada, descenso 1D; notebooks 1_04, 1_05) y Clase 4
  (MSE, regla delta, entrenamiento completo, Xavier, ADALINE, varias salidas; notebooks 1_06, 1_07, 1_08).
- Nuevos: docs/GUIA_PASO_A_PASO_CLASE3.md y CLASE4.md, docs/practica_03.py y practica_04.py (con asserts),
  entregables/Clase3_* y Clase4_* (guía PDF, diapositivas PDF y PPTX), notebooks/output/.gitkeep (1_05 guarda ahí).
- Clave local (no publicar, en .gitignore): soluciones_docente_m3.py. 1_07: ~100 épocas → exactitud 0.775; 1000 → 0.725.
- Ojo en 1_07: `weights += ...` (en el lugar); con `weights = weights + ...` la neurona no ve el cambio.
- PLAN_CLASE3.md eliminado (reemplazado por las guías). Siguiente: módulo 4, redes multicapa y retropropagación (1_09–1_11).

## Actualización (2026-11-10): guía por notebook (los 17)
- docs/guias_notebooks/: README (índice) + NB_<notebook>.md para los 17 notebooks; PDFs en entregables/guias_notebooks/
  y combinado en entregables/Guias_de_los_notebooks.pdf (46 págs). md_to_pdf.py ahora acepta varios .md → un PDF.
- notebooks/23_opt_lr_decay.ipynb: el original estaba VACÍO; se creó uno nuevo (decaimiento escalonado/inverso/exponencial).
- notebooks/1_03_2: se agregó n_classes=2 a DecisionBoundaryDisplay (scikit-learn 1.9 lo exige).
- Clave local (gitignored): soluciones_docente_notebooks.py rellena y EJECUTA los 17 notebooks (nbclient) →
  notebooks_resueltos/*.ipynb + RESUMEN.txt. Todos corren sin errores. Valores de las guías salen de ahí.
- Hallazgos: 1_11 imprime la pérdida con solo el último ejemplo (bug del original); 22 con lr 0.03 el descenso simple
  diverge y momentum converge; 3_2 entrena bien solo con normalizar+centrar+vectorizar+momentum (ECM 31600→29, kernel≈Sobel).
- El Python del sistema (3.13 de la Store) perdió sus paquetes una vez; se reinstalaron con pip.
