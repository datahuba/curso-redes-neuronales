"""Genera las diapositivas de las clases en PowerPoint (16:9).

Uso:  python tools/build_decks.py            -> entregables/Clase1_Diapositivas.pptx y Clase2_Diapositivas.pptx
Luego: powershell -File tools/export_pdf.ps1  -> PDF (y PNG de revisión) con PowerPoint
"""
import math
import os
import sys

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt
from lxml import etree

# ---------------------------------------------------------------- paleta
NAVY = RGBColor(0x14, 0x21, 0x3D)
CREAM = RGBColor(0xF7, 0xF5, 0xEF)
CARD = RGBColor(0xFF, 0xFD, 0xF8)
BORDER = RGBColor(0xE2, 0xDE, 0xD3)
BAND = RGBColor(0xEF, 0xEB, 0xE1)
ORANGE = RGBColor(0xC4, 0x62, 0x1D)
AMBER = RGBColor(0xF2, 0xA6, 0x5A)
BLUE = RGBColor(0x2F, 0x6F, 0xB0)
LBLUE = RGBColor(0x7F, 0xB0, 0xE0)
INK = RGBColor(0x14, 0x21, 0x3D)
GRAY = RGBColor(0x4A, 0x55, 0x68)
MUTED = RGBColor(0x8F, 0x9B, 0xB3)
SOFT = RGBColor(0xBF, 0xC8, 0xD8)
CODEBG = RGBColor(0x0D, 0x16, 0x29)
CODEFG = RGBColor(0xE6, 0xEA, 0xF2)
PALEORANGE = RGBColor(0xFB, 0xE3, 0xCF)
WHITE = RGBColor(0xFF, 0xF8, 0xF0)

SANS = "Segoe UI"
MONO = "Consolas"
W, H = 13.333, 7.5
LM, RM = 0.75, 12.58          # márgenes izquierdo/derecho
CW = RM - LM                  # ancho útil


# ---------------------------------------------------------------- helpers
class Deck:
    def __init__(self, footer):
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = Inches(W), Inches(H)
        self.footer = footer
        self.with_footer = []

    def slide(self, dark=False, notes="", footer=True):
        s = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        s.background.fill.solid()
        s.background.fill.fore_color.rgb = NAVY if dark else CREAM
        if notes:
            s.notes_slide.notes_text_frame.text = notes
        s._dark = dark
        self.with_footer.append(footer)
        return s

    def save(self, path):
        n = len(self.prs.slides)
        for i, (s, f) in enumerate(zip(self.prs.slides, self.with_footer), 1):
            if not f:
                continue
            c = getattr(s, "_footer", MUTED if s._dark else GRAY)
            text(s, LM, 6.95, 8, 0.35, self.footer, 11, c)
            text(s, RM - 2, 6.95, 2, 0.35, f"{i} / {n}", 11, c, align=PP_ALIGN.RIGHT)
        self.prs.save(path)
        return n


def _runs(p, spec, size, color, bold, font):
    """spec: str | (str, dict) | [str | (str, dict), ...]"""
    items = spec if isinstance(spec, list) else [spec]
    for it in items:
        t, o = (it, {}) if isinstance(it, str) else it
        r = p.add_run()
        r.text = t
        f = r.font
        f.size = Pt(o.get("size", size))
        f.name = o.get("font", font)
        f.bold = o.get("bold", bold)
        f.italic = o.get("italic", False)
        f.color.rgb = o.get("color", color)


def text(s, x, y, w, h, paras, size=20, color=GRAY, bold=False, font=SANS,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, fill=None, space=6, line=1.1, margin=0.08):
    box = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is not None:
        box.fill.solid()
        box.fill.fore_color.rgb = fill
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for side in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, side, Inches(margin))
    lines = paras if isinstance(paras, list) and not isinstance(paras, Runs) else [paras]
    for i, spec in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(space)
        p.line_spacing = line
        _runs(p, spec, size, color, bold, font)
    return box


class Runs(list):
    """Marca una lista como 'una sola línea con varios estilos'."""
    _runs = True


def rect(s, x, y, w, h, fill, line=None, rounded=True, radius=0.08, lw=1.0):
    shp = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE,
                             Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(lw)
    if rounded:
        shp.adjustments[0] = radius
    shp.shadow.inherit = False
    shp.text_frame.text = ""
    return shp


def shape(s, kind, x, y, w, h, fill, label="", size=18, color=CREAM, bold=True, line=None, lw=1.5):
    shp = s.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(lw)
    shp.shadow.inherit = False
    tf = shp.text_frame
    tf.word_wrap = True
    for side in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, side, Inches(0.03))
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    if label:
        _runs(p, label, size, color, bold, SANS)
    return shp


def arrow(s, x1, y1, x2, y2, color=GRAY, width=2.0, head=True, dash=False, tail=False):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color
    c.line.width = Pt(width)
    ln = c.line._get_or_add_ln()
    if dash:
        d = etree.SubElement(ln, qn("a:prstDash"))
        d.set("val", "dash")
    if tail:
        e = etree.SubElement(ln, qn("a:headEnd"))
        e.set("type", "oval")
    if head:
        e = etree.SubElement(ln, qn("a:tailEnd"))
        e.set("type", "triangle")
        e.set("w", "med")
        e.set("h", "med")
    return c


def polyline(s, pts, color, width=2.5, dash=False):
    """pts en pulgadas."""
    fb = s.shapes.build_freeform(Inches(pts[0][0]), Inches(pts[0][1]), scale=1.0)
    fb.add_line_segments([(Inches(x), Inches(y)) for x, y in pts[1:]], close=False)
    shp = fb.convert_to_shape()
    shp.fill.background()
    shp.line.color.rgb = color
    shp.line.width = Pt(width)
    if dash:
        ln = shp.line._get_or_add_ln()
        d = etree.SubElement(ln, qn("a:prstDash"))
        d.set("val", "dash")
    shp.shadow.inherit = False
    return shp


def title(s, t, eyebrow=None, dark=None):
    dark = s._dark if dark is None else dark
    y = 0.62
    if eyebrow:
        text(s, LM, 0.38, CW, 0.4, eyebrow.upper(), 14, AMBER if dark else BLUE, True)
        y = 0.75
    rect(s, LM - 0.28, y + 0.14, 0.09, 0.6, ORANGE if not dark else AMBER, rounded=False)
    text(s, LM, y, CW, 0.9, t, 34, CREAM if dark else INK, True)


def card(s, x, y, w, h, head, body, accent=ORANGE, size=18, head_size=22, fill=CARD, kicker=None):
    rect(s, x, y, w, h, fill, BORDER, radius=0.05)
    rect(s, x, y, w, 0.08, accent, rounded=False)
    yy = y + 0.2
    if kicker:
        text(s, x + 0.2, yy, w - 0.4, 0.35, kicker, 14, accent, True)
        yy += 0.35
    text(s, x + 0.2, yy, w - 0.4, 0.55, head, head_size, INK, True)
    text(s, x + 0.2, yy + 0.6, w - 0.4, h - (yy - y) - 0.7, body, size, GRAY)


def table(s, x, y, w, rows, size=18, col_w=None, row_h=0.46, highlight=None, dark=False, align=None):
    n, m = len(rows), len(rows[0])
    t = s.shapes.add_table(n, m, Inches(x), Inches(y), Inches(w), Inches(row_h * n)).table
    if col_w:
        for j, cw in enumerate(col_w):
            t.columns[j].width = Inches(cw)
    for i in range(n):
        t.rows[i].height = Inches(row_h)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = t.cell(i, j)
            c.margin_left = c.margin_right = Inches(0.12)
            c.margin_top = c.margin_bottom = Inches(0.05)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            c.fill.solid()
            if i == 0:
                c.fill.fore_color.rgb = ORANGE if dark else NAVY
            elif highlight and i in highlight:
                c.fill.fore_color.rgb = PALEORANGE
            elif dark:
                c.fill.fore_color.rgb = RGBColor(0x1C, 0x2C, 0x4F) if i % 2 else RGBColor(0x22, 0x34, 0x5C)
            else:
                c.fill.fore_color.rgb = CARD if i % 2 else BAND
            tf = c.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = ""
            if align and align[j]:
                p.alignment = align[j]
            col = CREAM if (i == 0 or dark) else INK
            _runs(p, val if not isinstance(val, str) else [(val, {})], size, col, i == 0, SANS)
    return t


def code(s, x, y, w, h, src, size=16):
    rect(s, x, y, w, h, CODEBG, RGBColor(0x2A, 0x3A, 0x5C), radius=0.04)
    box = s.shapes.add_textbox(Inches(x + 0.15), Inches(y + 0.15), Inches(w - 0.3), Inches(h - 0.3))
    tf = box.text_frame
    tf.word_wrap = True
    for i, line in enumerate(src.strip("\n").splitlines()):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(1)
        cpos = line.find("#")
        parts = [(line, CODEFG)] if cpos < 0 else [(line[:cpos], CODEFG), (line[cpos:], MUTED)]
        for t, col in parts:
            if not t:
                continue
            r = p.add_run()
            r.text = t
            r.font.size, r.font.name, r.font.color.rgb = Pt(size), MONO, col
        if not line:
            r = p.add_run()
            r.text = " "
            r.font.size = Pt(size)
    return box


def bullets(items, mark="•"):
    return [Runs([(f"{mark}  ", {"color": ORANGE, "bold": True})] + (list(i) if isinstance(i, Runs) else [(i, {})]))
            for i in items]


B = lambda t: (t, {"bold": True})                       # noqa: E731
C = lambda t, c: (t, {"color": c, "bold": True})        # noqa: E731


def cover(d, kicker, t1, t2, sub, notes):
    s = d.slide(True, notes, footer=False)
    rect(s, 0, 0, 0.35, H, ORANGE, rounded=False)
    text(s, 1.0, 1.55, 11, 0.5, kicker, 20, AMBER, True)
    text(s, 1.0, 2.15, 11.3, 2.4, [t1, t2], 54, CREAM, True, line=1.0, space=0)
    text(s, 1.0, 4.45, 11, 0.7, sub, 24, SOFT)
    text(s, 1.0, 6.55, 11.5, 0.4,
         "github.com/datahuba/curso-redes-neuronales  ·  Basado en el curso del Dr. J. Irving Vasquez (jivg.org)",
         12, MUTED)
    return s


# ================================================================ CLASE 1
def clase1():
    d = Deck("Introducción a las Redes Neuronales  ·  Clase 1")

    cover(d, "CLASE 1  ·  INTRODUCCIÓN", "Introducción a las", "Redes Neuronales",
          "Presentación del curso, herramientas, IA y aprendizaje automático",
          "Bienvenida. Curso introductorio: entender cómo funcionan las redes por dentro, sus fundamentos "
          "teóricos e implementarlas desde conceptos simples. Es la base para el aprendizaje profundo.")

    # 2 agenda
    s = d.slide(notes="Corresponde a los primeros 4 videos del curso. Duración aprox. 2 h 15 min con descanso.")
    title(s, "Agenda de hoy")
    items = [("01", "Presentación del curso", "Motivación y temario", ORANGE),
             ("02", "Instalar los ejercicios", "Anaconda, Git, VS Code, NumPy", ORANGE),
             ("03", "IA y redes neuronales", "Definiciones, test de Turing, alcances", BLUE),
             ("04", "El aprendizaje automático", "Definición, tareas y tipos", BLUE)]
    for k, (n, h, b, c) in enumerate(items):
        x, y = LM + (k % 2) * 6.0, 1.95 + (k // 2) * 2.35
        card(s, x, y, 5.8, 2.1, h, b, c, size=18, head_size=24, kicker=n)

    # 3 objetivos
    s = d.slide(notes="Lee los objetivos. Al final de la clase pide que ellos digan si los cumplieron.")
    title(s, "Al terminar la clase podrás…")
    objs = [("1", "Explicar qué es la IA", "y dónde encajan las redes neuronales dentro de ella."),
            ("2", "Distinguir tareas y tipos", "de aprendizaje automático: regresión, clasificación, refuerzo…"),
            ("3", "Tener tu computadora lista", "para resolver los ejercicios del curso en Python.")]
    for k, (n, h, b) in enumerate(objs):
        x = LM + k * 3.98
        rect(s, x, 2.0, 3.8, 3.9, CARD, BORDER, radius=0.05)
        shape(s, MSO_SHAPE.OVAL, x + 0.3, 2.3, 0.8, 0.8, ORANGE, n, 26)
        text(s, x + 0.3, 3.35, 3.2, 0.9, h, 24, INK, True)
        text(s, x + 0.3, 4.3, 3.2, 1.5, b, 18, GRAY)

    # 4 motivación
    s = d.slide(notes="Antes de mostrarla: lluvia de ideas de 5 minutos. ¿Qué aplicación con IA usaron hoy? "
                      "Recomienda el canal Two Minute Papers.")
    title(s, "Ya las usas todos los días")
    apps = [("Vehículos", "Conducción autónoma y asistida"), ("Lenguaje", "Asistentes, traductores, chatbots"),
            ("Imagen", "Filtros de TikTok, mejora de fotos"), ("Salud", "Diagnóstico por imagen médica"),
            ("Videojuegos", "Renderizado acelerado"), ("Refuerzo", "Agentes que dominan juegos"),
            ("Generativa", "DALL·E, Stable Diffusion"), ("Robótica", "Percepción y control")]
    for k, (h, b) in enumerate(apps):
        x, y = LM + (k % 4) * 2.98, 1.9 + (k // 4) * 2.0
        card(s, x, y, 2.83, 1.8, h, b, BLUE if k % 2 else ORANGE, size=16, head_size=20)
    text(s, LM, 6.05, CW, 0.6, "Funcionan por detrás en todas partes: conviene saber cómo operan.", 22, ORANGE, True)

    # 5 temario
    s = d.slide(notes="Recorre los módulos. Quien sienta que le falta base, que empiece por Preliminares. "
                      "Cómo trabajamos cada tema: libro, explicación, papel, notebook.")
    title(s, "¿Qué veremos en el curso?")
    mods = [("1", "Introducción", "IA y aprendizaje automático (hoy)"),
            ("2", "Principios", "McCulloch y Pitts, perceptrón"),
            ("3", "Red neuronal simple", "Activaciones, descenso por gradiente"),
            ("4", "Redes multicapa", "Retropropagación"),
            ("5", "Preliminares", "Cálculo, álgebra, probabilidad, Python (opcional)")]
    for k, (n, h, b) in enumerate(mods):
        x = LM + k * 2.38
        rect(s, x, 1.95, 2.25, 2.9, CARD, BORDER, radius=0.05)
        shape(s, MSO_SHAPE.OVAL, x + 0.2, 2.2, 0.62, 0.62, ORANGE if k == 0 else BLUE, n, 20)
        text(s, x + 0.15, 3.0, 2.0, 0.8, h, 19, INK, True)
        text(s, x + 0.15, 3.75, 2.0, 1.1, b, 15, GRAY)
    text(s, LM, 5.2, CW, 0.4, "CÓMO TRABAJAMOS CADA TEMA", 14, BLUE, True)
    steps = ["Libro", "Explicación", "Ejercicio en papel", "Notebook en Python"]
    for k, st in enumerate(steps):
        shape(s, MSO_SHAPE.CHEVRON if k else MSO_SHAPE.PENTAGON, LM + k * 2.95, 5.65, 3.0, 0.75,
              NAVY if k < 3 else ORANGE, st, 17)

    # 6 dos formas
    s = d.slide(notes="Los ejercicios son notebooks con instrucciones: se rellena código. Usamos NumPy a pie para "
                      "entender por dentro, en lugar de una función mágica como .fit().")
    title(s, "Dos formas de hacer los ejercicios", "Herramientas")
    text(s, LM, 1.85, CW, 0.6, Runs([("Rellenas el código con Python y NumPy ", {}),
                                     ("“a pie”", {"bold": True}), (", sin un simple .fit().", {})]), 20)
    card(s, LM, 2.65, 5.8, 2.9, "1 · Google Colab",
         bullets(["Abres el notebook en el navegador.", Runs([B("Ventaja: "), ("no hay que instalar nada.", {})]),
                  "Ideal como plan B."]), BLUE, size=19, head_size=26)
    card(s, LM + 6.0, 2.65, 5.8, 2.9, "2 · En tu computadora",
         bullets(["Anaconda + Git + VS Code.", Runs([B("Ventaja: "), ("experiencia real de desarrollo.", {})]),
                  "Es la opción recomendada."]), ORANGE, size=19, head_size=26)
    text(s, LM, 5.85, CW, 0.5, Runs([("Repositorio del curso:  ", {}), ("github.com/datahuba/curso-redes-neuronales",
                                                                     {"bold": True, "color": INK})]), 19)

    # 7 instalar programas
    s = d.slide(notes="Pasos 1 a 3 de la guía. Si ya los instalaron en casa, pasa a la siguiente. "
                      "Git: después de instalarlo hay que abrir una terminal nueva.")
    title(s, "Instalación (1/2): tres programas", "Herramientas")
    progs = [("1", "Anaconda", "anaconda.com/download", "Python y ambientes. Opción “Just Me”; no marcar PATH."),
             ("2", "Git", "git-scm.com/download/win", "Descargar el código del curso. Todo “Next”."),
             ("3", "VS Code", "code.visualstudio.com", "Editor. Instalar extensiones Python y Jupyter.")]
    for k, (n, h, url, b) in enumerate(progs):
        x = LM + k * 3.98
        rect(s, x, 1.95, 3.8, 4.1, CARD, BORDER, radius=0.05)
        shape(s, MSO_SHAPE.OVAL, x + 0.3, 2.25, 0.75, 0.75, ORANGE, n, 24)
        text(s, x + 0.3, 3.2, 3.3, 0.6, h, 28, INK, True)
        text(s, x + 0.3, 3.85, 3.3, 0.5, url, 15, BLUE, True, MONO)
        text(s, x + 0.3, 4.45, 3.3, 1.5, b, 18, GRAY)
    text(s, LM, 6.25, CW, 0.5, "Unos 5 GB libres y permisos de administrador. Anaconda pesa ~900 MB: descárgalo antes.",
         17, GRAY)

    # 8 comandos
    s = d.slide(True, notes="Pasos 4 a 7 de la guía, en vivo. nni = neural network introduction. Si mkdir dice que la "
                            "carpeta existe, no pasa nada. Termina cuando todos vean envs\\nni en la verificación final.")
    title(s, "Instalación (2/2): los comandos", "Todo en Anaconda PowerShell Prompt")
    code(s, LM, 1.85, 7.3, 3.75, """# 4. Crear y activar el ambiente
conda create --name nni python=3.11
conda activate nni

# 5. Descargar el curso
cd ~
mkdir projects
cd projects
git clone https://github.com/datahuba/curso-redes-neuronales.git
cd curso-redes-neuronales

# 6. Instalar los paquetes
pip install -r requirements.txt""", 13)
    text(s, 8.35, 1.85, 4.25, 0.4, "COMPRUEBA", 14, AMBER, True)
    checks = [Runs([("La línea empieza con ", {}), ("(nni)", {"bold": True, "font": MONO, "color": CREAM})]),
              Runs([("ls", {"bold": True, "font": MONO, "color": CREAM}), (" muestra docs y notebooks", {})]),
              Runs([("Termina con ", {}), ("Successfully installed", {"bold": True, "color": CREAM})])]
    text(s, 8.35, 2.3, 4.25, 2.2, bullets(checks, "✓"), 17, SOFT)
    text(s, 8.35, 4.45, 4.25, 0.4, "7. VS CODE", 14, AMBER, True)
    text(s, 8.35, 4.9, 4.25, 1.8, ["Abrir carpeta → curso-redes-neuronales",
                                   "Abrir un notebook → Select Kernel → nni"], 17, SOFT)

    # 9 qué es IA
    s = d.slide(notes="No hay una definición única. Russell y Norvig agrupan las definiciones. Ejemplo: una "
                      "calculadora no piensa como humano pero resuelve sumas perfecto. Lectura: capítulo 1.")
    title(s, "¿Qué es la inteligencia artificial?", "IA y redes neuronales")
    text(s, LM, 1.85, CW, 0.6, "No hay una definición única aceptada. Russell y Norvig las agrupan en dos enfoques:", 20)
    card(s, LM, 2.6, 5.8, 3.3, "Imitar al humano",
         ["Máquinas con mente: duplicar lo que hace el cerebro.", ("Riesgo: también copiamos sus errores.",
                                                                    {"italic": True})], BLUE, size=19, head_size=26)
    card(s, LM + 6.0, 2.6, 5.8, 3.3, "Actuar racionalmente",
         [Runs([B("Percibir → razonar → actuar"), (" para resolver el problema.", {})]),
          ("No tiene que funcionar como el cerebro.", {"italic": True})], ORANGE, size=19, head_size=26)
    text(s, LM, 6.15, CW, 0.5, "Lectura: Russell y Norvig, Inteligencia Artificial: un enfoque moderno, cap. 1", 16, GRAY)

    # 10 Turing
    s = d.slide(notes="Definición operacional: si el humano no distingue, la máquina pasa. Las redes con deep "
                      "learning ya cubren estas partes: espacio latente (representación), inferencia, decodificador "
                      "(síntesis) y pesos ajustables (aprendizaje).")
    title(s, "El test de Turing")
    text(s, LM, 1.8, CW, 0.9, Runs([("Definición ", {}), B("operacional"),
                                    (": si una persona que conversa por mensajes no distingue si del otro lado hay "
                                     "una máquina o una persona, la máquina pasa.", {})]), 20)
    text(s, LM, 2.85, CW, 0.4, "QUÉ NECESITA LA MÁQUINA", 14, BLUE, True)
    steps = [("Lenguaje natural", "Recibir el mensaje"), ("Representación", "Convertirlo en conocimiento"),
             ("Inferencia", "Generar la respuesta"), ("Síntesis", "Comunicarla al humano"),
             ("Aprendizaje", "Adaptarse a cada usuario")]
    for k, (h, b) in enumerate(steps):
        x = LM + k * 2.37
        shape(s, MSO_SHAPE.CHEVRON if k else MSO_SHAPE.PENTAGON, x, 3.35, 2.45, 0.95,
              ORANGE if k == 4 else NAVY, h, 14)
        text(s, x + 0.15, 4.4, 2.1, 0.9, b, 16, GRAY, align=PP_ALIGN.CENTER)
    rect(s, LM, 5.45, CW, 0.95, CARD, BORDER, radius=0.06)
    text(s, LM + 0.25, 5.45, CW - 0.5, 0.95, "Con el aprendizaje profundo, las redes neuronales ya cubren todas estas partes.",
         20, ORANGE, True, anchor=MSO_ANCHOR.MIDDLE)

    # 11 ejes
    s = d.slide(True, notes="En el video se dibujan tres ejes. Las redes quedan cargadas al eje operacional. "
                            "Explicabilidad y razonamiento son líneas de investigación abiertas.")
    title(s, "¿Qué tan lejos llegan las redes?")
    table(s, LM, 1.95, CW, [["Eje", "Qué incluye", "Redes neuronales"],
                            ["Operacional", "Controlar, jugar, reconocer, generar", [("Muy buenas", {"bold": True, "color": AMBER})]],
                            ["Razonamiento", "Representar conocimiento, inferir, conciencia", "Limitadas"],
                            ["Explicabilidad", "Garantizar cuándo funcionan y cuándo no", "Limitadas"]],
          20, [2.8, 5.8, 3.23], 0.75, dark=True)
    text(s, LM, 5.25, CW, 1.3, "Herramientas muy efectivas para resolver problemas, sin conciencia ni explicación "
                                 "completa. Por eso nos interesa cómo entrenarlas bien.", 22, SOFT)

    # 12 dónde encajan
    s = d.slide(notes="Cada recuadro está dentro del anterior. Deep learning: muchas capas, cada una extrae rasgos "
                      "más abstractos (bordes, formas, objetos). Mejora con más datos pero exige datos y cómputo.")
    title(s, "Dónde encajan las redes neuronales")
    boxes = [("Inteligencia Artificial", RGBColor(0xE8, 0xEC, 0xF4), INK),
             ("Aprendizaje Automático", RGBColor(0xC9, 0xD6, 0xEA), INK),
             ("Redes Neuronales", BLUE, CREAM), ("Aprendizaje Profundo", NAVY, AMBER)]
    for k, (lab, fill, col) in enumerate(boxes):
        x, y = LM + k * 0.45, 1.9 + k * 0.85
        rect(s, x, y, 7.0 - k * 0.9, 4.75 - k * 1.05, fill, radius=0.06)
        text(s, x + 0.2, y + 0.12, 6.0, 0.5, lab, 19, col, True)
    defs = [Runs([B("IA: "), ("tareas que asociamos con inteligencia.", {})]),
            Runs([B("Aprendizaje automático: "), ("aprende de datos sin programarse explícitamente.", {})]),
            Runs([B("Redes: "), ("unidades simples conectadas.", {})]),
            Runs([B("Deep learning: "), ("muchas capas; rasgos cada vez más abstractos.", {})])]
    text(s, 8.25, 1.95, 4.35, 4.7, defs, 18, GRAY, space=14)

    # 13 ML definición
    s = d.slide(notes="Ejemplo del ajedrez: imposible programar qué hacer en cada configuración del tablero; la "
                      "computadora debe aprender de la experiencia.")
    title(s, "El aprendizaje automático", "El aprendizaje automático")
    rect(s, LM, 1.95, 0.09, 1.6, ORANGE, rounded=False)
    text(s, LM + 0.3, 1.9, 11.4, 1.3, "“Dar a las computadoras la capacidad de aprender sin ser programadas explícitamente.”",
         28, INK, True, line=1.05)
    text(s, LM + 0.3, 3.15, 11, 0.4, "Arthur Samuel, 1959", 16, GRAY)
    trio = [("Tarea", "Ganar al ajedrez", BLUE), ("Experiencia", "Partidas jugadas, datos", BLUE),
            ("Desempeño", "Mejora tras observar: gana más seguido", ORANGE)]
    for k, (h, b, c) in enumerate(trio):
        card(s, LM + k * 3.98, 3.9, 3.8, 2.0, h, b, c, size=18, head_size=24)
    text(s, LM, 6.15, CW, 0.5, "Es imposible programar a mano qué hacer en cada posición del tablero.", 17, GRAY)

    # 14 regresión
    s = d.slide(notes="Los puntos son la experiencia (dataset). La función real no se conoce. Pregunta: ¿una curva "
                      "que pase exactamente por todos los puntos en zigzag es buena? No necesariamente.")
    title(s, "Tarea 1 · Regresión")
    px, py, pw, ph = LM, 1.9, 6.6, 4.55
    rect(s, px, py, pw, ph, CARD, BORDER, radius=0.03)
    ox, oy = px + 0.55, py + ph - 0.45
    arrow(s, ox, oy, px + pw - 0.25, oy, MUTED, 1.5)
    arrow(s, ox, oy, ox, py + 0.25, MUTED, 1.5)
    text(s, px + pw - 1.3, oy + 0.02, 1.1, 0.35, "entrada x", 12, GRAY)
    text(s, ox + 0.08, py + 0.15, 1.3, 0.35, "salida y", 12, GRAY)
    sx, sy = (pw - 1.0) / 10.0, (ph - 0.9) / 10.0
    P = lambda a, b: (ox + a * sx, oy - b * sy)             # noqa: E731
    f = lambda a: 1.2 + 0.55 * a + 0.9 * math.sin(a / 1.6)  # noqa: E731
    polyline(s, [P(a / 10, 0.4 + 0.83 * a / 10) for a in range(5, 101, 5)], RGBColor(0xB5, 0xB0, 0xA3), 2.0, dash=True)
    xs = [1, 2.2, 3.3, 4.4, 5.6, 6.7, 7.8, 9.0]
    noise = [0.5, -0.45, 0.4, -0.5, 0.35, -0.4, 0.45, -0.3]
    polyline(s, [P(a, f(a) + n) for a, n in zip(xs, noise)], RGBColor(0xB5, 0xB0, 0xA3), 1.6)
    polyline(s, [P(a / 10, f(a / 10)) for a in range(3, 98, 3)], BLUE, 3.5)
    for a, n in zip(xs, noise):
        x0, y0 = P(a, f(a) + n)
        shape(s, MSO_SHAPE.OVAL, x0 - 0.1, y0 - 0.1, 0.2, 0.2, ORANGE)
    leg = [Runs([C("● ", ORANGE), ("datos (experiencia)", {})]), Runs([C("━ ", BLUE), ("función real, desconocida", {})]),
           Runs([C("┅ ", MUTED), ("hipótesis candidatas", {})])]
    text(s, 7.65, 1.9, 4.95, 1.45, leg, 16, GRAY, space=3)
    text(s, 7.65, 3.4, 4.95, 3.1, [Runs([B("Hipótesis: "), ("una función f que relaciona entrada y salida.", {})]),
                                   Runs([B("Consistente: "), ("explica los datos observados.", {})]),
                                   Runs([("Pero queremos que también funcione con datos futuros: ", {}),
                                         ("generalización.", {"bold": True, "color": ORANGE})])], 18, GRAY, space=12)

    # 15 otras tareas
    s = d.slide(notes="Clasificación: dataset Dogs vs Cats de Kaggle. Agrupamiento: media y varianza de cada grupo. "
                      "Reducción: de 2 ejes a 1 y un umbral separa. Generativo: rostros nuevos.")
    title(s, "Otras tareas")
    tasks = [("Clasificación", "Asignar una etiqueta de un conjunto predefinido {l₁…lₙ}. Foto → “perro” o “gato”."),
             ("Agrupamiento", "Sin etiquetas: encontrar grupos (media y varianza) por orejas, bigotes…"),
             ("Reducción de dimensionalidad", "Menos características. De 2 ejes a 1: un umbral separa las clases."),
             ("Modelado generativo", "Aprender la distribución y muestrear de ella: rostros, arte, imágenes nuevas.")]
    for k, (h, b) in enumerate(tasks):
        card(s, LM + (k % 2) * 6.0, 1.9 + (k // 2) * 2.45, 5.8, 2.25, h, b, BLUE, size=18, head_size=23)

    # 16 tipos
    s = d.slide(notes="Supervisado: figuras con su etiqueta; tras entrenar predice clase 1 conos, clase 3 esferas. "
                      "No supervisado: descubre que los cubos tienen seis caras y las esferas no tienen vértices.")
    title(s, "Tipos de aprendizaje")
    table(s, LM, 1.9, CW, [["Tipo", "Experiencia", "Qué aprende"],
                           ["Supervisado", "Pares (x, y) etiquetados: conos, cubos, esferas", "La función x → y"],
                           ["No supervisado", "Solo ejemplos, sin etiquetas", "Las distribuciones que agrupan"],
                           ["Por refuerzo", "No está disponible: se obtiene interactuando", "Qué acción tomar en cada estado"]],
          19, [2.6, 5.4, 3.83], 0.72)
    rect(s, LM, 5.15, CW, 1.3, CARD, BORDER, radius=0.05)
    rect(s, LM, 5.15, 0.09, 1.3, ORANGE, rounded=False)
    text(s, LM + 0.3, 5.2, CW - 0.5, 1.2, Runs([B("Entrenamiento"), (" con el dataset  →  ", {}), B("generalización"),
                                                (": acertar en ejemplos nunca vistos, como un auto autónomo en calles "
                                                 "nuevas.", {})]), 19, GRAY, anchor=MSO_ANCHOR.MIDDLE)

    # 17 refuerzo
    s = d.slide(notes="Al inicio pierde mucho; con la experiencia ajusta su regla estado → acción y termina ganando. "
                      "Las redes sirven para regresión, clasificación, reducción y generación.")
    title(s, "Aprendizaje por refuerzo")
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, LM, 2.3, 2.6, 2.0, NAVY, "Agente", 26)
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, LM + 4.6, 2.3, 2.6, 2.0, BLUE, "Ambiente", 26)
    arrow(s, LM + 2.6, 2.85, LM + 4.6, 2.85, ORANGE, 3)
    arrow(s, LM + 4.6, 3.75, LM + 2.6, 3.75, BLUE, 3)
    text(s, LM + 2.6, 2.35, 2.0, 0.45, "acción", 16, ORANGE, True, align=PP_ALIGN.CENTER)
    text(s, LM + 2.45, 3.85, 2.3, 0.8, ["estado +", "recompensa"], 16, BLUE, True, align=PP_ALIGN.CENTER, space=0)
    text(s, LM, 4.75, 7.2, 1.6, "Ejemplo: ajedrez. Mover una ficha (acción) cambia el tablero (estado); comer una pieza o "
                                "ganar da recompensa.", 17, GRAY)
    text(s, 8.35, 2.1, 4.25, 4.4, [Runs([B("Corto plazo: "), ("comer una pieza.", {})]),
                                   Runs([B("Largo plazo (horizonte): "), ("ganar la partida.", {})]),
                                   Runs([("Objetivo: ", {"bold": True, "color": ORANGE}),
                                         ("maximizar la recompensa acumulada.", {"color": ORANGE, "bold": True})])],
         19, GRAY, space=16)

    # 18 quiz
    s = d.slide(notes="Respuestas: 1) solo mide si pasa o no, sin importar cómo funciona. 2) operacional. "
                      "3) funcionar en ejemplos no vistos. 4) clasificación tiene etiquetas predefinidas, agrupamiento "
                      "no. 5) la recompensa acumulada.")
    s.background.fill.fore_color.rgb = ORANGE
    s._dark = True
    s._footer = WHITE
    title(s, "Quiz · 5 minutos")
    qs = ["¿Por qué el test de Turing es una definición operacional?",
          "¿En cuál de los tres ejes destacan las redes neuronales?", "¿Qué es generalizar?",
          "¿Diferencia entre clasificación y agrupamiento?", "¿Qué maximiza un agente de aprendizaje por refuerzo?"]
    text(s, LM, 1.95, CW, 4.6, [Runs([(f"{k + 1}.  ", {"bold": True, "color": NAVY}), (q, {})]) for k, q in enumerate(qs)],
         24, WHITE, space=16)

    # 19 cierre
    s = d.slide(True, notes="Próxima clase: la neurona de McCulloch y Pitts.")
    title(s, "Para la próxima clase")
    tareas = ["Tener el ambiente nni instalado y el repositorio clonado.",
              "Leer Russell y Norvig: cap. 1 y secciones 18.1 y 18.2.",
              "Leer Goodfellow et al., Deep Learning: sección 5.1."]
    for k, t in enumerate(tareas):
        y = 2.0 + k * 1.05
        shape(s, MSO_SHAPE.OVAL, LM, y, 0.65, 0.65, AMBER, str(k + 1), 20, NAVY)
        text(s, LM + 0.95, y, 10.8, 0.7, t, 22, CREAM, anchor=MSO_ANCHOR.MIDDLE)
    text(s, LM, 5.6, CW, 0.6, "Siguiente: las redes neuronales por dentro, la neurona de McCulloch y Pitts.", 20, SOFT)
    return d


# ================================================================ CLASE 2
def clase2():
    d = Deck("Introducción a las Redes Neuronales  ·  Clase 2")
    cover(d, "CLASE 2  ·  MÓDULO 2", "Principios de las", "redes neuronales",
          "De la neurona de McCulloch y Pitts al perceptrón",
          "Hoy construimos la primera pieza de una red neuronal: la neurona artificial.")

    # 2 agenda
    s = d.slide(notes="Duración aprox. 2 h 30 min con 10 min de descanso.")
    title(s, "Agenda de hoy")
    table(s, LM, 1.85, CW, [["Tiempo", "Tema"], ["0:00", "Repaso de la Clase 1"], ["0:05", "Modelos paramétricos"],
                            ["0:15", "Neurona de McCulloch y Pitts"], ["0:40", "Práctica: McCulloch y Pitts"],
                            ["1:00", "Descanso"], ["1:10", "El perceptrón"], ["1:30", "Regla de aprendizaje"],
                            ["1:50", "Práctica: perceptrón en Python"], ["2:20", "Cierre, quiz y tarea"]],
          18, [1.8, 10.03], 0.48, highlight=[5])

    # 3 objetivos
    s = d.slide(notes="Lee los objetivos; al cierre pide que digan cuáles cumplieron.")
    title(s, "Al terminar la clase podrás…")
    objs = [("Calcular a mano", "la salida de una neurona de McCulloch y Pitts y de un perceptrón."),
            ("Aplicar la regla", "de aprendizaje de Rosenblatt, paso a paso."),
            ("Explicar XOR", "por qué un perceptrón no puede aprenderlo."),
            ("Programar", "ambas neuronas en Python.")]
    for k, (h, b) in enumerate(objs):
        x = LM + k * 2.98
        rect(s, x, 2.0, 2.83, 3.9, CARD, BORDER, radius=0.05)
        shape(s, MSO_SHAPE.OVAL, x + 0.25, 2.3, 0.75, 0.75, ORANGE, str(k + 1), 24)
        text(s, x + 0.25, 3.3, 2.4, 0.9, h, 22, INK, True)
        text(s, x + 0.25, 4.15, 2.4, 1.7, b, 17, GRAY)

    # 4 repaso
    s = d.slide(notes="Pregunta antes de revelar. Hoy: la primera pieza de una red neuronal.")
    title(s, "Repaso de la Clase 1")
    card(s, LM, 1.95, 5.8, 2.6, "¿Aprendizaje supervisado?", "Aprender de pares (entrada x, etiqueta y).", BLUE,
         size=20, head_size=26)
    card(s, LM + 6.0, 1.95, 5.8, 2.6, "¿Generalizar?", "Acertar en ejemplos que nunca vio.", BLUE, size=20, head_size=26)
    text(s, LM, 5.0, CW, 1.0, "Hoy: la primera pieza de una red neuronal, la neurona artificial.", 26, ORANGE, True)

    # 5 paramétricos
    s = d.slide(notes="Dibuja tres rectas: (w=1,b=0), (w=2,b=1), (w=-1,b=3). Misma forma, distintos parámetros. "
                      "Aprender: |y - ŷ| < ε con ε cercano a cero.")
    title(s, "Modelos paramétricos", "Módulo 2 · Principios")
    text(s, LM, 1.95, 6.3, 1.0, "ŷ = Φθ(X)", 48, INK, True, MONO)
    table(s, LM, 3.1, 6.3, [["Símbolo", "Significa"], ["X", "La entrada (los datos)"], ["θ", "Los parámetros: las perillas"],
                            ["ŷ", "La predicción del modelo"], ["y", "La respuesta correcta"]], 18, [1.6, 4.7], 0.5)
    rect(s, 7.45, 1.95, 5.13, 4.6, NAVY, radius=0.05)
    text(s, 7.8, 2.25, 4.5, 0.5, "IDEA CENTRAL DEL CURSO", 14, AMBER, True)
    text(s, 7.8, 2.8, 4.5, 1.9, "Aprender = encontrar θ tal que ŷ ≈ y", 30, CREAM, True, line=1.05)
    text(s, 7.8, 4.65, 4.5, 1.6, ["Ejemplo: la recta ŷ = w·x + b", "En redes: θ = pesos W y sesgo b"], 19, SOFT, space=10)

    # 6 MyP diagrama
    s = d.slide(notes="1943: Warren McCulloch (neurocientífico) y Walter Pitts (lógico). Primera neurona artificial. "
                      "Notación de Minsky: flechas excitatorias, línea con circulito inhibitoria.")
    title(s, "Neurona de McCulloch y Pitts (1943)")
    cx, cy, r = 4.1, 4.05, 0.95
    shape(s, MSO_SHAPE.OVAL, cx - r, cy - r, 2 * r, 2 * r, NAVY, "u = 2", 24)
    for k, lab in enumerate(["e₁", "e₂"]):
        y = cy - 0.55 + k * 1.1
        text(s, 0.9, y - 0.25, 0.8, 0.5, lab, 22, INK, True)
        arrow(s, 1.6, y, cx - r * math.cos(math.asin((y - cy) / r)) - 0.02, y, BLUE, 3)
    text(s, 1.55, 5.75, 0.8, 0.5, "ι₁", 22, INK, True)
    ix, iy = cx - 0.55, cy + r * 0.83
    arrow(s, 2.2, 6.0, ix, iy, ORANGE, 3, head=False)
    shape(s, MSO_SHAPE.OVAL, ix - 0.14, iy - 0.14, 0.28, 0.28, CREAM, line=ORANGE, lw=3)
    arrow(s, cx + r, cy, cx + r + 1.3, cy, INK, 3)
    text(s, cx + r + 1.4, cy - 0.3, 0.8, 0.6, "ŷ", 28, INK, True)
    text(s, 0.9, 2.05, 6.3, 0.5, Runs([C("→ excitatoria   ", BLUE), C("⊸ inhibitoria", ORANGE)]), 16, GRAY)
    table(s, 7.75, 1.95, 4.83, [["Elemento", "Valores"], ["E: excitatorias", "0 o 1"], ["I: inhibitorias", "0 o 1"],
                                ["u: umbral", "0, 1, 2, …"], ["ŷ: salida", "0 o 1"]], 18, [2.6, 2.23], 0.55)
    text(s, 7.75, 5.0, 4.83, 1.5, "La primera neurona artificial: una simplificación de la neurona biológica.", 17, GRAY)

    # 7 reglas
    s = d.slide(notes="Analogía del portero: las inhibitorias son la lista negra; el umbral, cuántas invitaciones necesitas.")
    title(s, "Cómo decide la neurona")
    rules = [("1", "Alguna inhibitoria vale 1", "ŷ = 0", ORANGE), ("2", "Si no, Σ eᵢ ≥ u", "ŷ = 1", BLUE),
             ("3", "En cualquier otro caso", "ŷ = 0", MUTED)]
    for k, (n, h, out, c) in enumerate(rules):
        y = 1.95 + k * 1.2
        rect(s, LM, y, 7.2, 1.0, CARD, BORDER, radius=0.08)
        shape(s, MSO_SHAPE.OVAL, LM + 0.2, y + 0.18, 0.64, 0.64, c, n, 20)
        text(s, LM + 1.05, y, 4.6, 1.0, h, 21, INK, True, anchor=MSO_ANCHOR.MIDDLE)
        text(s, LM + 5.4, y, 1.7, 1.0, out, 22, c, True, MONO, anchor=MSO_ANCHOR.MIDDLE)
    text(s, LM, 5.65, 7.2, 0.8, "Las reglas se aplican en este orden.", 17, GRAY)
    rect(s, 8.35, 1.95, 4.23, 4.4, NAVY, radius=0.05)
    text(s, 8.65, 2.2, 3.7, 0.5, "ANALOGÍA", 14, AMBER, True)
    text(s, 8.65, 2.7, 3.7, 0.6, "Un portero de discoteca", 22, CREAM, True)
    text(s, 8.65, 3.45, 3.7, 2.8, ["Inhibitorias = lista negra: si estás, no entras.",
                                   "Si no, entras con al menos u invitaciones (excitatorias)."], 17, SOFT, space=12)

    # 8 compuertas
    s = d.slide(notes="Hazlo fila por fila preguntando a la clase. Ejemplo extra del libro: C(E={e1}, I={i1}, u=1) es "
                      "'e1 Y NO i1'.")
    title(s, "Compuertas lógicas con McCulloch y Pitts")
    table(s, LM, 1.95, 6.5, [["e₁", "e₂", "Σ", "AND (u=2)", "OR (u=1)"], ["0", "0", "0", "0", "0"], ["0", "1", "1", "0", "1"],
                             ["1", "0", "1", "0", "1"], ["1", "1", "2", "1", "1"]], 19, [0.9, 0.9, 0.9, 1.9, 1.9], 0.6,
          highlight=[4], align=[PP_ALIGN.CENTER] * 5)
    table(s, 7.55, 1.95, 5.03, [["Compuerta", "Configuración"], ["AND", "u = n"], ["OR", "u = 1"], ["≥ k de n", "u = k"],
                                ["NOT", "E = ∅, 1 inhibitoria, u = 0"]], 18, [1.6, 3.43], 0.6)
    text(s, LM, 5.35, CW, 1.0, Runs([B("NOT: "), ("sin excitatorias la suma es 0 ≥ u = 0, así que se activa… salvo que la "
                                                  "inhibitoria valga 1.", {})]), 18, GRAY)

    # 9 limitaciones + ejercicios
    s = d.slide(notes="Respuestas: 1) u = 2. 2) 0,0,0,1 (AND). 3) Siempre 0. Pregunta las limitaciones antes de mostrarlas.")
    title(s, "Limitaciones y ejercicios")
    card(s, LM, 1.95, 5.8, 3.1, "Le falta…", bullets([Runs([B("Pesos: "), ("todas las entradas valen igual.", {})]),
                                                    Runs([B("Valores reales: "), ("solo acepta 0 o 1.", {})]),
                                                    Runs([B("Aprender: "), ("el umbral se fija a mano.", {})])]),
         ORANGE, size=19, head_size=26)
    card(s, LM + 6.0, 1.95, 5.8, 3.1, "En papel · 5 min",
         ["1.  Umbral para “al menos 2 de 3”.", "2.  Tabla de C(E={e₁,e₂}, I=∅, u=2).",
          "3.  C(E={e₁,e₂}, I={ι₁}, u=1) con ι₁ = 1."], BLUE, size=19, head_size=26)
    rect(s, LM, 5.35, CW, 0.95, NAVY, radius=0.08)
    text(s, LM + 0.3, 5.35, CW - 0.6, 0.95, "La limitación más importante: no aprende. Eso lo resuelve el perceptrón →",
         20, AMBER, True, anchor=MSO_ANCHOR.MIDDLE)

    # 10 práctica MyP
    s = d.slide(True, notes="Pistas: recorrer I primero (si hay un 1 devuelve 0), luego sumar E con un for y comparar con "
                            "u. Error típico: con E vacío y u = 0 la neurona se activa.")
    title(s, "Práctica · notebooks/1_01_mcculloch_pitts", "20 min · 3 puntos")
    text(s, LM, 1.9, 5.6, 3.2, [Runs([C("TODO 1 · 2 pts   ", AMBER), ("neuronaMyP(E, I, u) sin NumPy", {})]),
                                Runs([C("TODO 2 · 1 pt   ", AMBER), ("leer E, I y u arbitrarios", {})]),
                                "Traduce las 3 reglas al código, en el mismo orden."], 19, SOFT, space=14)
    code(s, 6.75, 1.9, 5.83, 2.55, """# comprobaciones
neuronaMyP([], [0], 0)     # 1
neuronaMyP([], [1], 0)     # 0
neuronaMyP([1, 1], [], 2)  # 1
neuronaMyP([1, 0], [], 2)  # 0
neuronaMyP([1], [0], 1)    # 1""", 17)
    text(s, LM, 5.55, CW, 0.8, "Sin Python: abre el notebook en Google Colab.", 18, MUTED)

    # 11 descanso
    s = d.slide(True, footer=False)
    text(s, LM, 2.7, CW, 1.2, "Descanso · 10 min", 54, CREAM, True, align=PP_ALIGN.CENTER)
    text(s, LM, 3.9, CW, 0.6, "Después: el perceptrón", 22, AMBER, align=PP_ALIGN.CENTER)

    # 12 perceptrón comparación
    s = d.slide(notes="Rosenblatt 1958. El primero fue una máquina física con potenciómetros y fotoceldas como ojos; "
                      "ajustaba sus pesos al equivocarse. Dendritas = entradas, núcleo = suma, axón = salida.")
    title(s, "El perceptrón (Rosenblatt, 1958)")
    table(s, LM, 1.95, CW, [["", "McCulloch y Pitts", "Perceptrón"], ["Entradas", "Solo 0 o 1", "Números reales"],
                            ["Importancia", "Todas iguales", "Un peso wᵢ por entrada"],
                            ["Desplazamiento", "Umbral u fijo", "Sesgo b ajustable"],
                            ["¿Aprende?", "No", [("Sí", {"bold": True, "color": ORANGE})]]],
          20, [2.9, 4.46, 4.47], 0.68, highlight=[4])
    text(s, LM, 5.6, CW, 0.8, "El primero fue una máquina física con fotoceldas como “ojos” que ajustaba sus pesos al equivocarse.",
         17, GRAY)

    # 13 modelo diagrama
    s = d.slide(notes="Paso 1: combinación lineal. Paso 2: activación escalón. Truco del sesgo: x0 = 1 con peso b, "
                      "así h = W·X. Variante: función signo devuelve -1 en lugar de 0.")
    title(s, "El modelo en dos pasos")
    xs_y = [2.45, 3.65, 4.85]
    sx_, sy_, sr = 4.15, 3.65, 0.55
    for k, y in enumerate(xs_y):
        shape(s, MSO_SHAPE.OVAL, 0.85, y - 0.38, 0.76, 0.76, BLUE, f"x{'₁₂₃'[k]}", 20)
        ang = math.atan2(sy_ - y, sx_ - 1.61)
        arrow(s, 1.61, y, sx_ - sr * math.cos(ang), sy_ - sr * math.sin(ang), GRAY, 2.2)
        text(s, 2.45, [2.33, 3.22, 4.42][k], 0.8, 0.4, f"w{'₁₂₃'[k]}", 16, ORANGE, True)
    shape(s, MSO_SHAPE.OVAL, sx_ - sr, sy_ - sr, 2 * sr, 2 * sr, NAVY, "Σ", 28)
    text(s, sx_ - 0.3, 1.9, 0.6, 0.4, "b", 18, ORANGE, True, align=PP_ALIGN.CENTER)
    arrow(s, sx_, 2.3, sx_, sy_ - sr, ORANGE, 2.2)
    rect(s, 5.45, 3.15, 1.3, 1.0, CARD, NAVY, radius=0.1, lw=2)
    polyline(s, [(5.65, 3.9), (6.1, 3.9), (6.1, 3.4), (6.55, 3.4)], NAVY, 3)
    arrow(s, sx_ + sr, sy_, 5.45, sy_, GRAY, 2.2)
    text(s, sx_ + sr - 0.05, sy_ - 0.48, 0.8, 0.4, "h", 18, INK, True, align=PP_ALIGN.CENTER)
    arrow(s, 6.75, sy_, 7.45, sy_, GRAY, 2.2)
    text(s, 7.45, sy_ - 0.35, 0.7, 0.7, "ŷ", 28, INK, True)
    text(s, 5.25, 4.3, 1.8, 0.4, "escalón", 15, GRAY, align=PP_ALIGN.CENTER)
    card(s, 8.35, 1.9, 4.23, 2.2, "1 · Combinación lineal", [("h = Σ wᵢ·xᵢ + b", {"font": MONO, "color": INK})],
         BLUE, size=22, head_size=20)
    card(s, 8.35, 4.3, 4.23, 2.2, "2 · Activación escalón",
         [("ŷ = 1 si h ≥ 0", {"font": MONO, "color": INK}), ("ŷ = 0 si h < 0", {"font": MONO, "color": INK})],
         BLUE, size=22, head_size=20)
    text(s, LM, 5.35, 7.2, 1.2, "Truco: una entrada extra x₀ = 1 con peso b; así el sesgo es “un peso más”.", 17, GRAY)

    # 14 ejemplo + analogía
    s = d.slide(notes="Ejemplo del libro (cap. 03-fundamentos/03). Analogía: sol y descansado h = 1, salgo; sol y "
                      "cansado h = -2, no salgo.")
    title(s, "Ejemplos: calcular la salida")
    rect(s, LM, 1.95, 5.8, 4.5, CARD, BORDER, radius=0.05)
    rect(s, LM, 1.95, 5.8, 0.08, BLUE, rounded=False)
    text(s, LM + 0.25, 2.15, 5.3, 0.5, "Del libro", 22, INK, True)
    text(s, LM + 0.25, 2.75, 5.3, 3.6, [("W = [0.7, −0.3, 0.4] · b = 0", {"font": MONO}), ("X = [8, 5, 6]", {"font": MONO}),
                                        ("h = 0.7·8 − 0.3·5 + 0.4·6", {"font": MONO}), ("  = 5.6 − 1.5 + 2.4 = 6.5", {"font": MONO}),
                                        Runs([("ŷ = f(6.5) = ", {"font": MONO}), ("1", {"font": MONO, "bold": True, "color": ORANGE})])],
         19, INK, space=8)
    rect(s, LM + 6.0, 1.95, 5.83, 4.5, CARD, BORDER, radius=0.05)
    rect(s, LM + 6.0, 1.95, 5.83, 0.08, ORANGE, rounded=False)
    text(s, LM + 6.25, 2.15, 5.3, 0.5, "¿Salgo a correr?", 22, INK, True)
    text(s, LM + 6.25, 2.75, 5.4, 3.6, ["x₁ = ¿hace sol?  ·  x₂ = ¿estoy cansado?", "w = [2, −3] · b = −1",
                                        Runs([("Sol y descansado: h = 1 → ", {}), ("salgo", {"bold": True, "color": BLUE})]),
                                        Runs([("Sol y cansado: h = −2 → ", {}), ("no salgo", {"bold": True, "color": ORANGE})])],
         18, GRAY, space=12)

    # 15 geometría
    s = d.slide(notes="Antes de revelar XOR deja 2 minutos para que intenten trazar una recta. OR: w = [1,1], b = -0.5.")
    title(s, "El perceptrón traza una recta")

    def plot(x0, y0, size, pts, lab, line=None):
        rect(s, x0, y0, size, size, CARD, BORDER, radius=0.03)
        m = 0.55
        g = lambda a, b: (x0 + m + a * (size - 2 * m), y0 + size - m - b * (size - 2 * m))  # noqa: E731
        ax0, ay0 = g(-0.15, -0.15)
        arrow(s, ax0, ay0, x0 + size - 0.2, ay0, MUTED, 1.2)
        arrow(s, ax0, ay0, ax0, y0 + 0.2, MUTED, 1.2)
        text(s, x0 + size - 0.65, ay0 - 0.02, 0.5, 0.3, "x₁", 12, GRAY)
        text(s, ax0 - 0.4, y0 + 0.12, 0.4, 0.3, "x₂", 12, GRAY)
        if line:
            (a1, b1), (a2, b2) = line
            polyline(s, [g(a1, b1), g(a2, b2)], ORANGE, 3.5)
        for (a, b), cls in pts:
            px_, py_ = g(a, b)
            if cls:
                shape(s, MSO_SHAPE.RECTANGLE, px_ - 0.16, py_ - 0.16, 0.32, 0.32, ORANGE)
            else:
                shape(s, MSO_SHAPE.OVAL, px_ - 0.16, py_ - 0.16, 0.32, 0.32, BLUE)
        text(s, x0, y0 + size + 0.05, size, 0.45, lab, 18, INK, True, align=PP_ALIGN.CENTER)

    plot(LM, 1.85, 3.9, [((0, 0), 0), ((0, 1), 0), ((1, 0), 0), ((1, 1), 1)], "AND: separable",
         ((0.4, 1.1), (1.1, 0.4)))
    plot(LM + 4.25, 1.85, 3.9, [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 0)], "XOR: ¿una recta?")
    text(s, 9.2, 1.9, 3.38, 4.6, [("Frontera de decisión", {"bold": True, "color": INK}),
                                  ("w₁x₁ + w₂x₂ + b = 0", {"font": MONO, "color": INK}),
                                  Runs([B("AND: "), ("w = [1, 1], b = −1.5", {})]), Runs([B("OR: "), ("w = [1, 1], b = −0.5", {})]),
                                  ("XOR: ninguna recta separa los cuadrados de los círculos.", {"bold": True, "color": ORANGE}),
                                  "→ no es linealmente separable."], 17, GRAY, space=10)
    text(s, LM, 6.3, 8.2, 0.4, Runs([C("■ ", ORANGE), ("clase 1     ", {}), C("● ", BLUE), ("clase 0", {})]), 14, GRAY)

    # 16 regla
    s = d.slide(notes="Paso 1: inicializar pesos aleatorios pequeños o en cero. Paso 2: aplicar la regla ejemplo por "
                      "ejemplo. Novikoff (1962): converge si los datos son linealmente separables.")
    title(s, "Regla de aprendizaje de Rosenblatt")
    rect(s, LM, 1.85, CW, 1.45, NAVY, radius=0.06)
    text(s, LM + 0.4, 1.85, CW - 0.8, 1.45, ["W ← W + η (y − ŷ) X", "b ← b + η (y − ŷ)"], 28, CREAM, True, MONO,
         anchor=MSO_ANCHOR.MIDDLE, space=2)
    table(s, LM, 3.55, CW, [["Caso", "Error y − ŷ", "Efecto"], ["Acertó", "0", "No cambia nada"],
                            ["Dijo 0, debía decir 1", "+1", "Suma η·X: h sube"],
                            ["Dijo 1, debía decir 0", "−1", "Resta η·X: h baja"]], 19, [4.4, 2.3, 5.13], 0.55)
    text(s, LM, 5.95, CW, 0.7, Runs([B("η"), (" = tasa de aprendizaje  ·  ", {}), B("época"),
                                     (" = una pasada por todo el dataset  ·  converge si los datos son linealmente separables",
                                      {})]), 16, GRAY)

    # 17 ejemplo regla
    s = d.slide(notes="Ejemplo del libro (cap. 04-aprendizaje/02). Resuélvelo en el pizarrón paso a paso.")
    title(s, "Ejemplo: un paso de aprendizaje")
    text(s, LM, 1.8, CW, 0.5, "X = [3, 5, 8] · y = 0 · η = 0.5 · W⁰ = [0.3, −0.4, 0.5] · b⁰ = 0.2", 19, GRAY, font=MONO)
    table(s, LM, 2.45, CW, [["#", "Cálculo"], ["1", "h = 0.9 − 2.0 + 4.0 + 0.2 = 3.1  →  ŷ = 1"],
                            ["2", "error = 0 − 1 = −1   (se equivocó)"],
                            ["3", "W¹ = W⁰ − 0.5·[3, 5, 8] = [−1.2, −2.9, −3.5]"], ["4", "b¹ = 0.2 − 0.5 = −0.3"],
                            ["5", "Comprobar: h = −46.4 < 0  →  ŷ = 0 = y  ✓"]], 20, [0.8, 11.03], 0.66, highlight=[5])

    # 18 ejercicios
    s = d.slide(notes="A: h = 0.3, ŷ = 1, e = -1, ΔW = [-0.1, -0.2], Δb = -0.1, W = [0.4, -0.5], b = 0.3. "
                      "B: 1350 presentaciones, 1323 repeticiones. C: w = [-1, -1], b = 1.5.")
    title(s, "Ejercicios en papel · 10 min")
    ex = [("A", ["w = [0.5, −0.3]", "b = 0.4 · η = 0.1", "X = [1, 2] · y = 0"], "¿ŷ? ¿error? ¿nuevos pesos?"),
          ("B", "50 épocas sobre 27 ejemplos.", "¿Cuántas presentaciones son repeticiones?"),
          ("C", "NAND vale 0 solo en (1, 1).", "Encuentra pesos y sesgo.")]
    for k, (n, a, b) in enumerate(ex):
        x = LM + k * 3.98
        rect(s, x, 1.95, 3.8, 4.4, CARD, BORDER, radius=0.05)
        shape(s, MSO_SHAPE.OVAL, x + 0.3, 2.25, 0.8, 0.8, ORANGE, n, 26)
        text(s, x + 0.3, 3.3, 3.25, 1.6, a, 19, INK)
        text(s, x + 0.3, 4.85, 3.25, 1.4, b, 18, ORANGE, True)

    # 19 código
    s = d.slide(True, notes="Demo en vivo con (nni) activo, dentro del repo: python docs/practica_02.py. AND y OR en 4 "
                            "épocas; XOR termina con convergió=False.")
    title(s, "El perceptrón en Python", "docs/practica_02.py")
    code(s, LM, 1.85, 7.9, 4.1, """def predecir(x, w, b):
    h = sum(wi * xi for wi, xi in zip(w, x)) + b
    return 1 if h >= 0 else 0

def entrenar(X, y, eta=0.1, epocas=100):
    w, b = [0.0] * len(X[0]), 0.0
    for _ in range(epocas):
        for xi, yi in zip(X, y):
            error = yi - predecir(xi, w, b)
            w = [wj + eta*error*xj for wj, xj in zip(w, xi)]
            b += eta * error
    return w, b""", 15)
    text(s, 8.95, 1.85, 3.63, 0.4, "EJECUTA", 14, AMBER, True)
    text(s, 8.95, 2.3, 3.63, 0.9, "python docs/practica_02.py", 16, CREAM, True, MONO)
    text(s, 8.95, 3.3, 3.63, 3.0, [Runs([C("AND, OR: ", CREAM), ("aprende en 4 épocas", {})]),
                                   Runs([C("XOR: ", AMBER), ("convergió=False tras 100 épocas", {})])], 17, SOFT, space=14)

    # 20 práctica notebooks
    s = d.slide(notes="En 1_03_2 con 3 épocas suele quedar incompleto: probar 20 a 50 épocas y eta entre 0.01 y 0.5. "
                      "Las soluciones solo están en la clave local del docente.")
    title(s, "Práctica · notebooks del perceptrón", "30 min")
    table(s, LM, 1.9, CW, [["Notebook", "Qué hacer", "Pts"], ["1_02_perceptron_AND", "Ajustar pesos a mano para AND", "—"],
                           ["1_03_1_perceptron_simple", "Combinación lineal sin np.dot, escalón, pesos de OR", "3"],
                           ["1_03_2_regla_de_aprendizaje", "Inicializar, pérdida SAE, regla, hiperparámetros", "4"]],
          18, [4.3, 6.53, 1.0], 0.62, align=[None, None, PP_ALIGN.CENTER])
    rect(s, LM, 4.7, CW, 1.6, CARD, BORDER, radius=0.05)
    text(s, LM + 0.3, 4.8, CW - 0.6, 1.4, [Runs([B("Comprueba 1_03_1: "), ("inputs [0.7, −0.3], weights [0.1, 0.8], "
                                                                        "bias −0.1 → h = −0.27 → salida 0", {})]),
                                          Runs([B("En 1_03_2: "), ("sube las épocas a 20–50 y mira cómo baja la pérdida.", {})])],
         17, GRAY, space=10)

    # 21 cierre
    s = d.slide(True, notes="Quiz de salida: qué tiene el perceptrón que no tiene MyP (pesos, reales, aprende); "
                            "inhibitoria activa (salida 0); si ŷ = y (no cambia); época (una pasada); XOR (no separable). "
                            "Minsky y Papert, Perceptrons (1969).")
    title(s, "Para llevar")
    take = ["Neurona = suma ponderada + activación.", "El perceptrón aprende corrigiendo pesos con el error.",
            "Solo separa clases con una recta."]
    for k, t in enumerate(take):
        y = 1.95 + k * 0.85
        shape(s, MSO_SHAPE.OVAL, LM, y, 0.6, 0.6, AMBER, str(k + 1), 18, NAVY)
        text(s, LM + 0.85, y - 0.03, 11, 0.65, t, 22, CREAM, anchor=MSO_ANCHOR.MIDDLE)
    rect(s, LM, 4.6, CW, 0.85, RGBColor(0x22, 0x34, 0x5C), radius=0.08)
    text(s, LM + 0.3, 4.6, CW - 0.6, 0.85, "¿Y XOR? Conectando neuronas en capas. Próximas clases.", 22, AMBER, True,
         anchor=MSO_ANCHOR.MIDDLE)
    text(s, LM, 5.65, CW, 1.0, [Runs([C("Tarea: ", CREAM), ("notebooks 1_01, 1_03_1 y 1_03_2 (10 pts)", {})]),
                                Runs([C("Leer: ", CREAM), ("libro, “Neurona artificial moderna”", {})])], 18, SOFT, space=4)
    return d


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "entregables"
    os.makedirs(out, exist_ok=True)
    for name, fn in [("Clase1_Diapositivas", clase1), ("Clase2_Diapositivas", clase2)]:
        path = os.path.join(out, name + ".pptx")
        print(path, fn().save(path), "diapositivas")
