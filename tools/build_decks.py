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


def title(s, t, eyebrow=None, dark=None, size=34):
    dark = s._dark if dark is None else dark
    y = 0.62
    if eyebrow:
        text(s, LM, 0.38, CW, 0.4, eyebrow.upper(), 14, AMBER if dark else BLUE, True)
        y = 0.75
    rect(s, LM - 0.28, y + 0.14, 0.09, 0.6, ORANGE if not dark else AMBER, rounded=False)
    text(s, LM, y, CW, 0.9, t, size, CREAM if dark else INK, True)


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


# ---------------------------------------------------------------- gráficas
def plotbox(s, x0, y0, w, h, xr, yr, fill=CARD, m=0.3, xlabel=None, ylabel=None):
    """Dibuja un marco con ejes y devuelve g(a, b) -> pulgadas."""
    rect(s, x0, y0, w, h, fill, BORDER, radius=0.03)

    def g(a, b):
        return (x0 + m + (a - xr[0]) / (xr[1] - xr[0]) * (w - 2 * m),
                y0 + h - m - (b - yr[0]) / (yr[1] - yr[0]) * (h - 2 * m))
    ya = 0 if yr[0] <= 0 <= yr[1] else yr[0]
    xa = 0 if xr[0] <= 0 <= xr[1] else xr[0]
    polyline(s, [g(xr[0], ya), g(xr[1], ya)], MUTED, 1.2)
    polyline(s, [g(xa, yr[0]), g(xa, yr[1])], MUTED, 1.2)
    if xlabel:
        px, py = g(xr[1], ya)
        text(s, px - 2.6, py + 0.02, 2.6, 0.3, xlabel, 11, GRAY, align=PP_ALIGN.RIGHT)
    if ylabel:
        px, py = g(xa, yr[1])
        text(s, px + 0.05, py - 0.05, 1.5, 0.3, ylabel, 11, GRAY)
    return g


def curve(s, g, fn, xr, yr, color, width=3.0, n=80, dash=False):
    seg = []
    for k in range(n + 1):
        a = xr[0] + (xr[1] - xr[0]) * k / n
        b = fn(a)
        if yr[0] - 1e-9 <= b <= yr[1] + 1e-9:
            seg.append(g(a, b))
        elif len(seg) > 1:
            polyline(s, seg, color, width, dash)
            seg = []
        else:
            seg = []
    if len(seg) > 1:
        polyline(s, seg, color, width, dash)


def dot(s, g, a, b, color, r=0.09):
    x, y = g(a, b)
    shape(s, MSO_SHAPE.OVAL, x - r, y - r, 2 * r, 2 * r, color)


def sig(h):
    return 1 / (1 + math.exp(-h))


def agenda(d, rows, highlight=None):
    s = d.slide(notes="Duración aprox. 2 h 30 min con 10 min de descanso.")
    title(s, "Agenda de hoy")
    rh = min(0.46, 4.75 / (len(rows) + 1))
    table(s, LM, 1.8, CW, [["Tiempo", "Tema"]] + rows, 18 if rh >= 0.45 else 16, [1.8, 10.03], rh, highlight=highlight)


def objetivos(d, objs, notes="Lee los objetivos; al cierre pide que digan cuáles cumplieron."):
    s = d.slide(notes=notes)
    title(s, "Al terminar la clase podrás…")
    n = len(objs)
    wcard = (CW - 0.15 * (n - 1)) / n
    for k, (h, b) in enumerate(objs):
        x = LM + k * (wcard + 0.15)
        rect(s, x, 2.0, wcard, 3.9, CARD, BORDER, radius=0.05)
        shape(s, MSO_SHAPE.OVAL, x + 0.22, 2.3, 0.7, 0.7, ORANGE, str(k + 1), 22)
        text(s, x + 0.2, 3.2, wcard - 0.35, 0.95, h, 20, INK, True)
        text(s, x + 0.2, 4.15, wcard - 0.35, 1.7, b, 16, GRAY)


def practica(d, nb, meta, todos, check, pistas="", notes="", extra=None, size=17):
    s = d.slide(True, notes=notes)
    title(s, f"Práctica · {nb}", meta, size=34 if len(nb) < 34 else 28)
    text(s, LM, 1.9, 6.0, 2.0, [Runs([C(t + "   ", AMBER), (b, {})]) for t, b in todos], size, SOFT, space=10)
    if pistas:
        text(s, LM, 3.95, 6.0, 1.3, pistas, 15, MUTED)
    code(s, 7.0, 1.9, 5.58, 3.0, check, 15)
    if extra:
        text(s, LM, 5.5, CW, 1.0, extra, 17, MUTED)
    return s


def descanso(d, siguiente):
    s = d.slide(True, footer=False)
    text(s, LM, 2.7, CW, 1.2, "Descanso · 10 min", 54, CREAM, True, align=PP_ALIGN.CENTER)
    text(s, LM, 3.9, CW, 0.6, f"Después: {siguiente}", 22, AMBER, align=PP_ALIGN.CENTER)


def cierre(d, take, highlight, tarea, leer, notes):
    s = d.slide(True, notes=notes)
    title(s, "Para llevar")
    for k, t in enumerate(take):
        y = 1.95 + k * 0.85
        shape(s, MSO_SHAPE.OVAL, LM, y, 0.6, 0.6, AMBER, str(k + 1), 18, NAVY)
        text(s, LM + 0.85, y - 0.03, 11, 0.65, t, 21, CREAM, anchor=MSO_ANCHOR.MIDDLE)
    rect(s, LM, 4.6, CW, 0.85, RGBColor(0x22, 0x34, 0x5C), radius=0.08)
    text(s, LM + 0.3, 4.6, CW - 0.6, 0.85, highlight, 21, AMBER, True, anchor=MSO_ANCHOR.MIDDLE)
    text(s, LM, 5.65, CW, 1.0, [Runs([C("Tarea: ", CREAM), (tarea, {})]), Runs([C("Leer: ", CREAM), (leer, {})])],
         18, SOFT, space=4)


# ================================================================ CLASE 3
def clase3():
    d = Deck("Introducción a las Redes Neuronales  ·  Clase 3")
    cover(d, "CLASE 3  ·  MÓDULO 3 (PARTE 1)", "Red neuronal simple:", "activación y gradiente",
          "Neurona moderna, funciones de activación y descenso por gradiente",
          "Hoy cambiamos el escalón por funciones suaves y aprendemos la herramienta para entrenar: el descenso por gradiente.")
    agenda(d, [["0:00", "Repaso de la Clase 2"], ["0:10", "Del escalón a la neurona moderna"], ["0:25", "¿Qué es una derivada?"],
               ["0:35", "Funciones de activación"], ["0:55", "Ejemplo a mano"], ["1:00", "Práctica: neurona con sigmoide"],
               ["1:20", "Descanso"], ["1:30", "Descenso por gradiente"], ["1:55", "Ejercicios en papel"],
               ["2:05", "Práctica: descenso por gradiente"], ["2:25", "Cierre y tarea"]], highlight=[7])
    objetivos(d, [("Distinguir", "la neurona moderna del perceptrón: activación continua."),
                  ("Calcular", "las activaciones lineal, sigmoide, tanh y ReLU."),
                  ("Explicar", "qué es una derivada: la pendiente."),
                  ("Aplicar", "el descenso por gradiente y elegir η."),
                  ("Programar", "una neurona y el descenso en Python.")])

    # 4 repaso
    s = d.slide(notes="Pregunta antes de revelar cada tarjeta.")
    title(s, "Repaso de la Clase 2")
    rep = [("¿Cómo calcula?", "h = Σ wᵢxᵢ + b y luego el escalón: 1 si h ≥ 0."),
           ("¿Cómo aprende?", "W ← W + η(y − ŷ)X: corrige con el error."), ("¿Qué no pudo?", "XOR: no es linealmente separable.")]
    for k, (h, b) in enumerate(rep):
        card(s, LM + k * 3.98, 1.95, 3.8, 2.6, h, b, BLUE, size=19, head_size=24)
    text(s, LM, 5.0, CW, 1.0, "Hoy: cambiar el escalón por algo suave y aprender a bajar montañas.", 24, ORANGE, True)

    # 5 escalón
    s = d.slide(notes="Analogía: buscar las llaves con alguien que solo dice sí o no, contra alguien que dice frío, tibio, "
                      "caliente. Una función suave da pistas.")
    title(s, "¿Qué tiene de malo el escalón?", "Del escalón a la neurona moderna")
    g = plotbox(s, LM, 1.95, 5.2, 3.9, (-4, 4), (-0.2, 1.25), xlabel="h", ylabel="ŷ")
    polyline(s, [g(-4, 0), g(0, 0), g(0, 1), g(4, 1)], ORANGE, 4)
    text(s, LM, 5.9, 5.2, 0.4, "Escalón: salta de 0 a 1 en h = 0", 15, GRAY, align=PP_ALIGN.CENTER)
    text(s, 6.4, 1.95, 6.18, 3.0, bullets([Runs([B("Todo o nada: "), ("h = −0.01 y h = −100 dan lo mismo.", {})]),
                                          Runs([B("Plano: "), ("mover un poco un peso casi nunca cambia la salida.", {})]),
                                          Runs([B("Salto: "), ("en h = 0 no hay pendiente definida.", {})])]), 19, GRAY, space=12)
    rect(s, 6.4, 4.75, 6.18, 1.4, NAVY, radius=0.06)
    text(s, 6.65, 4.75, 5.7, 1.4, "Buscar llaves con “sí / no” es difícil; con “frío… tibio… caliente” es fácil.",
         18, CREAM, True, anchor=MSO_ANCHOR.MIDDLE)

    # 6 neurona moderna
    s = d.slide(notes="Widrow y Hoff, 1960: ADALINE. Mismos dos pasos; la activación es continua y derivable. Se entrena "
                      "con la regla delta, que viene del descenso por gradiente.")
    title(s, "La neurona artificial moderna")
    card(s, LM, 1.95, 5.6, 2.1, "Widrow y Hoff, 1960", "ADALINE: ADAptive LInear NEuron.", BLUE, size=19, head_size=23)
    card(s, LM, 4.25, 5.6, 2.2, "Los mismos dos pasos",
         [("h = Σ wᵢxᵢ + b", {"font": MONO, "color": INK}), Runs([("ŷ = f(h)  con f ", {"font": MONO, "color": INK}),
                                                                  ("continua y derivable", {"bold": True, "color": ORANGE})])],
         ORANGE, size=19, head_size=23)
    g = plotbox(s, 6.6, 1.95, 5.98, 4.5, (-6, 6), (-0.15, 1.2), xlabel="h")
    polyline(s, [g(-6, 0), g(0, 0), g(0, 1), g(6, 1)], MUTED, 2.5, dash=True)
    curve(s, g, sig, (-6, 6), (-0.15, 1.2), BLUE, 4)
    text(s, 6.9, 2.05, 5.5, 0.6, Runs([C("━ sigmoide (suave)   ", BLUE), C("┅ escalón", MUTED)]), 15, GRAY)

    # 7 derivada
    s = d.slide(notes="No hace falta cálculo: la derivada es la pendiente. Dibuja tangentes en x = -3, 0, 3. Signo: hacia "
                      "dónde sube. Tamaño: qué tan empinada.")
    title(s, "¿Qué es una derivada?")
    g = plotbox(s, LM, 1.9, 6.2, 4.6, (-4, 4), (-1.5, 16), xlabel="x", ylabel="f(x) = x²")
    curve(s, g, lambda a: a * a, (-4, 4), (-1.5, 16), BLUE, 3.5)
    for x0, c in [(-3, ORANGE), (0, NAVY), (3, ORANGE)]:
        curve(s, g, lambda a, x0=x0: x0 * x0 + 2 * x0 * (a - x0), (x0 - 1.1, x0 + 1.1), (-1.5, 16), c, 2.5)
        dot(s, g, x0, x0 * x0, c, 0.1)
    text(s, 7.25, 1.9, 5.33, 1.6, Runs([B("Derivada = pendiente "), ("de la curva en un punto: cuánto sube si avanzas un "
                                                                     "poquito a la derecha.", {})]), 19, GRAY)
    table(s, 7.25, 3.55, 5.33, [["x", "−3", "0", "1", "3"], ["f′(x) = 2x", "−6", "0", "2", "6"]], 18,
          [1.73, 0.9, 0.9, 0.9, 0.9], 0.55, align=[None] + [PP_ALIGN.CENTER] * 4)
    text(s, 7.25, 4.85, 5.33, 1.6, [Runs([B("Signo: "), ("hacia dónde sube.", {})]),
                                    Runs([B("Tamaño: "), ("qué tan empinada está.", {})])], 18, GRAY, space=8)

    # 8 activaciones
    s = d.slide(notes="e ≈ 2.718. Lineal para regresión; sigmoide para probabilidades; tanh centrada en 0; ReLU la más usada "
                      "en redes profundas.")
    title(s, "Funciones de activación")
    acts = [("Lineal", lambda a: a, (-3, 3), "f(h) = h", "cualquier número"),
            ("Sigmoide", sig, (-0.2, 1.2), "1 / (1 + e⁻ʰ)", "entre 0 y 1"),
            ("tanh", math.tanh, (-1.2, 1.2), "(eʰ − e⁻ʰ)/(eʰ + e⁻ʰ)", "entre −1 y 1"),
            ("ReLU", lambda a: max(0.0, a), (-0.5, 3), "máx(0, h)", "0 o positivo")]
    for k, (nm, fn, yr, fx, rg) in enumerate(acts):
        x = LM + k * 2.98
        g = plotbox(s, x, 1.85, 2.83, 2.6, (-3, 3), yr, m=0.22)
        curve(s, g, fn, (-3, 3), yr, ORANGE if k % 2 else BLUE, 3.5)
        text(s, x, 4.55, 2.83, 0.45, nm, 20, INK, True)
        text(s, x, 5.0, 2.83, 0.45, fx, 14, INK, font=MONO)
        text(s, x, 5.45, 2.83, 0.45, rg, 15, GRAY)
    text(s, LM, 6.05, CW, 0.5, "e ≈ 2.718 (como π ≈ 3.14).  e⁻ʰ = “e elevado a menos h”.", 15, GRAY)

    # 9 tabla valores
    s = d.slide(notes="Calcula 2 o 3 casillas con calculadora. Que noten: la sigmoide nunca llega a 0 ni a 1; vale 0.5 en "
                      "h = 0; tanh es la sigmoide estirada entre -1 y 1.")
    title(s, "Tabla de valores")
    table(s, LM, 1.9, CW, [["h", "lineal", "sigmoide", "tanh", "ReLU"], ["−3", "−3", "0.0474", "−0.9951", "0"],
                           ["−1", "−1", "0.2689", "−0.7616", "0"], ["0", "0", "0.5", "0", "0"],
                           ["1", "1", "0.7311", "0.7616", "1"], ["3", "3", "0.9526", "0.9951", "3"]],
          20, [1.6, 2.5, 2.6, 2.6, 2.53], 0.6, highlight=[3], align=[PP_ALIGN.CENTER] * 5)
    text(s, LM, 5.75, CW, 0.7, "La sigmoide nunca llega a 0 ni a 1, y vale exactamente 0.5 cuando h = 0.", 19, ORANGE, True)

    # 10 sigmoide detalle
    s = d.slide(notes="Saturación: en los extremos la pendiente es casi 0 y aprende lento. Derivada sigma(1-sigma), máxima "
                      "0.25 en h = 0. Si todo fuera lineal, la cadena seguiría siendo una recta.")
    title(s, "La sigmoide en detalle")
    g = plotbox(s, LM, 1.9, 6.2, 4.5, (-6, 6), (-0.05, 1.1), xlabel="h")
    curve(s, g, sig, (-6, 6), (-0.05, 1.1), BLUE, 4)
    curve(s, g, lambda a: sig(a) * (1 - sig(a)), (-6, 6), (-0.05, 1.1), ORANGE, 4)
    text(s, LM + 0.4, 1.95, 5.5, 0.4, Runs([C("━ σ(h)   ", BLUE), C("━ σ′(h)", ORANGE)]), 15, GRAY)
    text(s, LM + 0.25, 5.95, 5.9, 0.4, "Saturación: en los extremos la pendiente ≈ 0", 14, GRAY)
    rect(s, 7.25, 1.9, 5.33, 1.3, NAVY, radius=0.06)
    text(s, 7.25, 1.9, 5.33, 1.3, "σ′(h) = σ(h) · (1 − σ(h))", 24, CREAM, True, MONO, align=PP_ALIGN.CENTER,
         anchor=MSO_ANCHOR.MIDDLE)
    text(s, 7.25, 3.45, 5.33, 3.0, [Runs([B("Máxima en h = 0: "), ("σ′(0) = 0.25.", {})]),
                                    Runs([B("Saturación: "), ("con h muy grande o muy negativo aprende lento.", {})]),
                                    Runs([B("No lineal: "), ("si todo fuera lineal, la red entera seguiría siendo una recta.",
                                                             {})])], 18, GRAY, space=12)

    # 11 ejemplo a mano
    s = d.slide(notes="Mismo ejemplo que verifica el notebook 1_04. Con el escalón la salida sería solo 0.")
    title(s, "Ejemplo a mano")
    text(s, LM, 1.85, CW, 0.5, "X = [0.7, −0.3]  ·  W = [0.1, 0.8]  ·  b = −0.1", 20, GRAY, font=MONO)
    table(s, LM, 2.5, CW, [["Paso", "Cálculo"], ["1. Combinación lineal", "h = 0.07 − 0.24 − 0.1 = −0.27"],
                           ["2. Sigmoide", "e^0.27 ≈ 1.3100  →  σ(−0.27) = 1 / 2.3100 ≈ 0.4329"],
                           ["3. Con tanh", "tanh(−0.27) ≈ −0.2636"], ["Con el escalón", "h < 0  →  ŷ = 0 (sin más información)"]],
          19, [3.4, 8.43], 0.62, highlight=[2])
    text(s, LM, 5.85, CW, 0.6, "La sigmoide dice algo más rico: “0.43, casi en la frontera”.", 20, ORANGE, True)

    practica(d, "1_04_red_neuronal_simple", "notebooks · 20 min · 3 puntos",
             [("TODO 1 pt", "sigmoide(h) con np.exp(-h)"), ("TODO 1 pt", "Neurona: combinacion_lineal y forward"),
              ("TODO 1 pt", "tanh y comparación con la sigmoide")],
             "# comprobaciones\nOutput: 0.4329        # sigmoide\ntanh(-0.27) = -0.2636\n\n# error típico: np.exp(h)\n# sin el signo menos -> 0.5671",
             "Pistas: np.dot(self.W, X) hace la suma de productos; dentro de la clase usa self.W y self.b.",
             "Mismo ejemplo de la diapositiva 11.", extra="Sin Python: abre el notebook en Google Colab.")
    descanso(d, "el descenso por gradiente")

    # 14 montaña
    s = d.slide(notes="En redes, la función será el error y la variable los pesos. Analogía: bajar de noche sintiendo la "
                      "pendiente con los pies.")
    title(s, "Descenso por gradiente", "Bajar la montaña a oscuras")
    g = plotbox(s, LM, 1.9, 6.6, 4.5, (-1, 7), (-0.5, 6))
    f = lambda a: 0.18 * (a - 3.2) ** 2 + 0.6 * math.sin(a * 1.3) + 0.8  # noqa: E731
    curve(s, g, f, (-0.8, 6.8), (-0.5, 6), NAVY, 4)
    for a in [5.9, 5.1, 4.3]:
        dot(s, g, a, f(a), ORANGE, 0.12)
    x1, y1 = g(5.9, f(5.9) + 0.6)
    x2, y2 = g(4.4, f(4.4) + 0.6)
    arrow(s, x1, y1, x2, y2, ORANGE, 3)
    text(s, 7.7, 1.9, 4.88, 1.5, Runs([B("Objetivo: "), ("encontrar el x que hace f(x) lo más pequeña posible.", {})]),
         19, GRAY)
    text(s, 7.7, 3.3, 4.88, 1.5, Runs([B("En redes: "), ("f es el error y x son los pesos.", {})]), 19, GRAY)
    rect(s, 7.7, 4.55, 4.88, 1.85, NAVY, radius=0.06)
    text(s, 7.95, 4.55, 4.4, 1.85, "De noche, sin linterna: sientes con los pies hacia dónde baja y das un paso.",
         18, CREAM, True, anchor=MSO_ANCHOR.MIDDLE)

    # 15 regla
    s = d.slide(notes="La derivada apunta hacia donde sube; queremos bajar, por eso el signo menos. Algoritmo: inicial, "
                      "pendiente, actualizar, repetir.")
    title(s, "La regla del descenso")
    rect(s, LM, 1.85, CW, 1.2, NAVY, radius=0.06)
    text(s, LM, 1.85, CW, 1.2, "x  ←  x − η · f′(x)", 36, CREAM, True, MONO, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    table(s, LM, 3.3, 6.2, [["Símbolo", "Significa"], ["x", "Dónde estás parado"], ["f′(x)", "La pendiente: hacia dónde sube"],
                            ["η (eta)", "Tasa de aprendizaje: tamaño del paso"]], 17, [1.6, 4.6], 0.55)
    card(s, 7.25, 3.3, 5.33, 3.1, "¿Por qué el signo menos?",
         ["La derivada apunta hacia donde la función sube.", Runs([("Queremos bajar: vamos en ", {}),
                                                                   ("contra de la pendiente.", {"bold": True})])],
         ORANGE, size=18, head_size=22)

    # 16 ejemplo x²
    s = d.slide(notes="Desde x = -2: -2 - 0.1*(-4) = -1.6; f baja de 4 a 2.56. Desde 5: los pasos se acortan solos porque la "
                      "pendiente disminuye.")
    title(s, "Ejemplo: f(x) = x², η = 0.1")
    g = plotbox(s, LM, 1.85, 5.6, 4.6, (-1, 5.6), (-1.5, 27), xlabel="x")
    curve(s, g, lambda a: a * a, (-1, 5.3), (-1.5, 27), BLUE, 3.5)
    pts = [5, 4, 3.2, 2.56, 2.048, 1.6384]
    for a, b_ in zip(pts, pts[1:]):
        polyline(s, [g(a, a * a), g(b_, b_ * b_)], ORANGE, 2)
    for a in pts:
        dot(s, g, a, a * a, ORANGE, 0.1)
    table(s, 6.65, 1.85, 5.93, [["x", "f′(x) = 2x", "x − 0.1·f′(x)"], ["5", "10", "4"], ["4", "8", "3.2"],
                                ["3.2", "6.4", "2.56"], ["2.56", "5.12", "2.048"], ["2.048", "4.096", "1.6384"]],
          18, [1.6, 2.0, 2.33], 0.52, align=[PP_ALIGN.CENTER] * 3)
    text(s, 6.65, 5.15, 5.93, 1.3, "Los pasos se acortan solos al acercarse al fondo: la pendiente es más pequeña ahí.",
         17, ORANGE, True)

    # 17 tasa de aprendizaje
    s = d.slide(notes="0.01 lento; 0.1 bien; 0.5 llega de un salto solo en este problema; 0.9 oscila; 1.1 diverge. η es un "
                      "hiperparámetro: lo elegimos nosotros.")
    title(s, "La tasa de aprendizaje η")
    for k, (eta, lab, col) in enumerate([(0.01, "η = 0.01 · muy lento", BLUE), (0.1, "η = 0.1 · bien", BLUE),
                                         (0.9, "η = 0.9 · oscila", ORANGE), (1.1, "η = 1.1 · diverge", ORANGE)]):
        x = LM + k * 2.98
        g = plotbox(s, x, 1.85, 2.83, 2.5, (-9, 9), (-3, 80), m=0.18)
        curve(s, g, lambda a: a * a, (-9, 9), (-3, 80), MUTED, 2)
        xs_ = [5.0]
        for _ in range(3):
            xs_.append(xs_[-1] - eta * 2 * xs_[-1])
        for a, b_ in zip(xs_, xs_[1:]):
            polyline(s, [g(a, a * a), g(b_, b_ * b_)], col, 1.8)
        for a in xs_:
            dot(s, g, a, a * a, col, 0.07)
        text(s, x, 4.4, 2.83, 0.45, lab, 16, INK, True, align=PP_ALIGN.CENTER)
    table(s, LM, 5.0, CW, [["η", "0.01", "0.1", "0.5", "0.9", "1.1"],
                           ["Desde x = 5, cinco pasos", "4.52", "1.64", "0 (de un salto)", "−1.64 (oscila)", "−12.44 (diverge)"]],
          16, [3.03, 1.4, 1.4, 2.0, 2.0, 2.0], 0.5, align=[None] + [PP_ALIGN.CENTER] * 5)
    text(s, LM, 6.15, CW, 0.5, "η es un hiperparámetro: lo elegimos nosotros. Ni muy pequeño ni muy grande.", 16, GRAY, True)

    # 18 ejercicios
    s = d.slide(notes="1) 1.5 y 0.75. 2) 10, 5.6, 2.96, 1.376, 0.4256, -0.1446, -0.4868 (tiende a -1). 3) 0.5 y 0.25.")
    title(s, "Ejercicios en papel · 10 min")
    ex = [("1", ["f(x) = x²", "x₀ = 3 · η = 0.25"], "Calcula dos pasos."),
          ("2", ["f(x) = 2x + x²", "x₀ = 10 · η = 0.2", "Pista: f′(x) = 2 + 2x"], "Calcula 6 valores."),
          ("3", ["Sigmoide en h = 0"], "¿Cuánto vale σ(0)? ¿Y σ′(0)?")]
    for k, (n, a, b) in enumerate(ex):
        x = LM + k * 3.98
        rect(s, x, 1.95, 3.8, 4.4, CARD, BORDER, radius=0.05)
        shape(s, MSO_SHAPE.OVAL, x + 0.3, 2.25, 0.8, 0.8, ORANGE, n, 26)
        text(s, x + 0.3, 3.3, 3.25, 1.6, a, 19, INK)
        text(s, x + 0.3, 4.95, 3.25, 1.3, b, 18, ORANGE, True)

    practica(d, "1_05_descenso_por_gradiente_1D", "notebooks · 15 min · 2 puntos  ·  + docs/practica_03.py",
             [("TODO 1 pt", "gradient_descent_update: la regla del descenso"),
              ("TODO 1 pt", "ciclo while hasta error < 1e-3; contar iteraciones")],
             "# historial esperado\n[5, 4.0, 3.2, 2.56, 2.048, 1.6384]\n\n# iteraciones con 1e-3:\n# |x_nuevo - x| -> 32   f(x) -> 23",
             "Pistas: la derivada ya existe como df(x). Para detenerse, usa while y un contador.",
             "0.01 lento; 0.1 bien; 1.1 diverge.", extra="Demo: python docs/practica_03.py --graficar   (activaciones y cinco valores de η)")

    cierre(d, ["Neurona moderna: activación suave y derivable.", "Derivada = pendiente: dice hacia dónde sube.",
               "Descenso: x ← x − η·f′(x), con η ni muy grande ni muy pequeña."],
           "Próxima clase: bajar por el error de la red moviendo los pesos.",
           "notebooks 1_04 y 1_05 (5 pts)", "libro, “Descenso por gradiente” (aprendizaje)",
           "Quiz de salida: activación continua; sigmoide 0 a 1, tanh -1 a 1; derivada = pendiente; signo menos para bajar; "
           "η grande oscila o diverge.")
    return d


# ================================================================ CLASE 4
def clase4():
    d = Deck("Introducción a las Redes Neuronales  ·  Clase 4")
    cover(d, "CLASE 4  ·  MÓDULO 3 (PARTE 2)", "Entrenar una", "neurona",
          "Regla delta, entrenamiento completo, ADALINE y redes de varias salidas",
          "Hoy usamos el descenso por gradiente de la clase 3 para entrenar los pesos de una neurona.")
    agenda(d, [["0:00", "Repaso de la Clase 3"], ["0:10", "Medir el error"], ["0:25", "La regla delta"],
               ["0:50", "Práctica: un paso del descenso"], ["1:10", "Descanso"], ["1:20", "Entrenamiento completo e inicialización"],
               ["1:35", "Práctica: entrenar una neurona"], ["2:00", "ADALINE"], ["2:08", "Red con varias salidas"],
               ["2:20", "Quiz y cierre"]], highlight=[5])
    objetivos(d, [("Medir", "el error de una red con el MSE."), ("Aplicar", "un paso de la regla delta a mano."),
                  ("Entrenar", "una neurona completa y medir su exactitud."),
                  ("Inicializar", "los pesos al azar con Xavier."), ("Calcular", "una capa con varias salidas.")])

    # 4 repaso
    s = d.slide(notes="Pregunta antes de revelar. Hoy en vez de x² bajamos por el error, moviendo los pesos.")
    title(s, "Repaso de la Clase 3")
    rep = [("¿Sigmoide?", "Convierte h en un número entre 0 y 1, suave."), ("¿Derivada?", "La pendiente: hacia dónde sube."),
           ("¿Descenso?", "x ← x − η·f′(x)")]
    for k, (h, b) in enumerate(rep):
        card(s, LM + k * 3.98, 1.95, 3.8, 2.6, h, b, BLUE, size=19, head_size=24)
    text(s, LM, 5.0, CW, 1.0, "Hoy: bajar por el error de la red moviendo los pesos. Eso es entrenar.", 24, ORANGE, True)

    # 5 medir error
    s = d.slide(notes="Al cuadrado para que + y - no se cancelen y para castigar más los errores grandes. Error, pérdida y "
                      "costo son sinónimos.")
    title(s, "Medir el error", "Pérdida · loss · función de costo")
    table(s, LM, 1.9, 6.6, [["Medida", "Fórmula"], ["Error residual", "e = y − ŷ"], ["SSE", "Σ (y − ŷ)²"],
                            ["MSE (promedio)", "(1/m) Σ (y − ŷ)²"]], 19, [2.6, 4.0], 0.6)
    text(s, LM, 4.5, 6.6, 1.9, [Runs([B("¿Por qué al cuadrado? "), ("+1 y −1 no se cancelan, y los errores grandes pesan "
                                                                   "más.", {})])], 18, GRAY)
    card(s, 7.6, 1.9, 4.98, 4.45, "Ejemplo",
         [("y = [1, 0, 1]", {"font": MONO, "color": INK}), ("ŷ = [0.8, 0.3, 0.6]", {"font": MONO, "color": INK}),
          "errores²: 0.04, 0.09, 0.16", Runs([B("SSE = 0.29")]), Runs([("MSE = 0.29 / 3 ≈ ", {}),
                                                                      ("0.0967", {"bold": True, "color": ORANGE})])],
         ORANGE, size=18, head_size=22)

    # 6 montaña del error
    s = d.slide(notes="Si dibujamos el error contra un peso sale un valle. Entrenar = bajar ese valle: es la clase 3 con w en "
                      "lugar de x.")
    title(s, "La pérdida es una montaña")
    g = plotbox(s, LM, 1.9, 6.6, 4.5, (-1, 5), (-0.3, 5), xlabel="peso w", ylabel="error E")
    curve(s, g, lambda a: 0.45 * (a - 2.2) ** 2 + 0.3, (-1, 5), (-0.3, 5), BLUE, 4)
    for a in [4.6, 3.8, 3.1, 2.6]:
        dot(s, g, a, 0.45 * (a - 2.2) ** 2 + 0.3, ORANGE, 0.11)
    dot(s, g, 2.2, 0.3, NAVY, 0.12)
    text(s, LM + 3.6, 2.0, 2.9, 0.35, Runs([C("● ", NAVY), ("pesos óptimos   ", {}), C("● ", ORANGE), ("pasos", {})]),
         13, GRAY, align=PP_ALIGN.RIGHT)
    rect(s, 7.6, 1.9, 4.98, 2.0, NAVY, radius=0.06)
    text(s, 7.85, 1.9, 4.5, 2.0, "Entrenar = bajar al valle del error moviendo los pesos.", 22, CREAM, True,
         anchor=MSO_ANCHOR.MIDDLE)
    text(s, 7.6, 4.2, 4.98, 2.2, ["Es lo mismo de la clase 3:", Runs([("x  →  ", {}), B("peso w")]),
                                  Runs([("f(x)  →  ", {}), B("error E")])], 19, GRAY, space=8)

    # 7 cadena
    s = d.slide(notes="Efecto dominó: cambiar w cambia h, que cambia ŷ, que cambia E. Se multiplican las derivadas de cada "
                      "eslabón: regla de la cadena. Los dos signos menos se cancelan.")
    title(s, "¿Cuánto cambia el error si muevo un peso?")
    chain = [("wᵢ", NAVY), ("h", BLUE), ("ŷ = f(h)", BLUE), ("E = ½(y − ŷ)²", ORANGE)]
    for k, (lab, col) in enumerate(chain):
        x = LM + k * 3.05
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, 1.95, 2.55, 0.95, col, lab, 19)
        if k < 3:
            arrow(s, x + 2.55, 2.42, x + 3.05, 2.42, GRAY, 2.5)
    for k, lab in enumerate(["xᵢ", "f′(h)", "−(y − ŷ)"]):
        text(s, LM + k * 3.05 + 1.9, 3.0, 1.9, 0.45, lab, 17, ORANGE, True, MONO, align=PP_ALIGN.CENTER)
    text(s, LM, 3.55, CW, 0.5, "Regla de la cadena: se multiplican los efectos de cada eslabón", 16, GRAY,
         align=PP_ALIGN.CENTER)
    rect(s, LM, 4.25, CW, 0.95, CARD, BORDER, radius=0.06)
    text(s, LM, 4.25, CW, 0.95, "∂E/∂wᵢ = −(y − ŷ) · f′(h) · xᵢ", 26, INK, True, MONO, align=PP_ALIGN.CENTER,
         anchor=MSO_ANCHOR.MIDDLE)
    rect(s, LM, 5.4, CW, 0.95, NAVY, radius=0.06)
    text(s, LM, 5.4, CW, 0.95, "w ← w − η·∂E/∂w   ⇒   wᵢ ← wᵢ + η (y − ŷ) f′(h) xᵢ", 22, CREAM, True, MONO,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    # 8 regla delta
    s = d.slide(notes="Delta se lee delta; por eso regla delta (Widrow y Hoff). Con sigmoide f'(h) = ŷ(1 - ŷ).")
    title(s, "La regla delta en tres pasos")
    steps = [("1 · Término de error", "δ = (y − ŷ) · f′(h)", "Cuánto y hacia dónde corregir"),
             ("2 · Incremento", "Δwᵢ = η · δ · xᵢ", "Δb = η · δ"),
             ("3 · Actualización", "wᵢ ← wᵢ + Δwᵢ", "b ← b + Δb")]
    for k, (h, f_, b) in enumerate(steps):
        x = LM + k * 3.98
        shape(s, MSO_SHAPE.CHEVRON if k else MSO_SHAPE.PENTAGON, x, 1.95, 4.0, 0.9, ORANGE if k == 0 else NAVY, h, 18)
        rect(s, x, 3.05, 3.8, 2.3, CARD, BORDER, radius=0.05)
        text(s, x + 0.2, 3.25, 3.4, 0.8, f_, 20, INK, True, MONO)
        text(s, x + 0.2, 4.2, 3.4, 1.0, b, 17, GRAY, font=MONO if k else SANS)
    text(s, LM, 5.7, CW, 0.7, Runs([("Con la sigmoide:  ", {}), ("f′(h) = ŷ · (1 − ŷ)", {"font": MONO, "bold": True,
                                                                                         "color": ORANGE})]), 20, GRAY)

    # 9 ejemplo
    s = d.slide(notes="Mismos números del notebook 1_06. La pérdida 1/2(y - ŷ)² baja de 0.0905 a 0.0404.")
    title(s, "Ejemplo: un paso de la regla delta")
    text(s, LM, 1.8, CW, 0.5, "x = [1, 1] · y = 1 · w = [0.1, 0.2] · b = 0 · η = 2 · sigmoide", 18, GRAY, font=MONO)
    table(s, LM, 2.4, CW, [["Paso", "Cálculo"], ["Predicción", "h = 0.3  →  ŷ = σ(0.3) ≈ 0.5744"],
                           ["Derivada", "f′(h) = 0.5744 · 0.4256 ≈ 0.2445"], ["Término de error", "δ = (1 − 0.5744) · 0.2445 ≈ 0.1040"],
                           ["Incremento", "Δw = 2 · 0.1040 · [1, 1] ≈ [0.2081, 0.2081]  ·  Δb ≈ 0.2081"],
                           ["Actualización", "w ≈ [0.3081, 0.4081]  ·  b ≈ 0.2081"],
                           ["Comprobar", "ŷ ≈ 0.7159  ·  pérdida 0.0905 → 0.0404  ✓"]], 18, [2.9, 8.93], 0.55, highlight=[6])

    # 10 comparación
    s = d.slide(notes="Se parecen mucho; la regla delta añade f'(h), que sale de derivar.")
    title(s, "Perceptrón vs. regla delta")
    table(s, LM, 1.95, CW, [["", "Perceptrón (Clase 2)", "Regla delta (hoy)"], ["Activación", "Escalón", "Continua (sigmoide, lineal…)"],
                            ["Corrección", "η · (y − ŷ) · x", [("η · (y − ŷ) · ", {}), ("f′(h)", {"bold": True, "color": ORANGE}), (" · x", {})]],
                            ["De dónde sale", "Intuición de Rosenblatt", "Descenso por gradiente"],
                            ["El error indica", "Solo si acertó", "Qué tan lejos estuvo"]], 19, [2.9, 4.46, 4.47], 0.7)
    text(s, LM, 5.75, CW, 0.6, "¡Casi la misma fórmula! La diferencia es la pendiente de la activación.", 20, ORANGE, True)

    practica(d, "1_06_descenso_unpaso", "notebooks · 20 min · 3 puntos",
             [("TODO 1 pt", "error_term: δ = (y − ŷ)·f′(h)"), ("TODO 1 pt", "incremento: η·δ·X"),
              ("TODO 1 pt", "actualizacion: sumar a W y b")],
             "# comprobaciones\nSalida: 0.5744\nTérmino de error: 0.1040\nIncremento: [0.2081 0.2081]\nPesos actualizados: [0.3081 0.4081]",
             "Pistas: h con neurona.combinacion_lineal(x), ŷ con neurona.forward(x), f′ con sigmoid_prime(h).",
             "Mismos números de la diapositiva 9.", extra="Al final: vuelve a predecir. Debe dar ≈ 0.7159, más cerca de y = 1.")
    descanso(d, "entrenar con todos los datos")

    # 13 algoritmo
    s = d.slide(notes="Descenso por lotes: una actualización por época con el promedio de los incrementos.")
    title(s, "El algoritmo completo")
    pasos = [("1", "Inicializar los pesos al azar (Xavier)."),
             ("2", "Para cada época: incrementos acumulados = 0."),
             ("3", "Para cada ejemplo: ŷ, δ y sumar δ·x al acumulado."),
             ("4", "Actualizar: w += η · acumulado / n_ejemplos."),
             ("5", "Medir el error (MSE) y repetir."),
             ("6", "Al final: exactitud con datos de prueba.")]
    for k, (n, t) in enumerate(pasos):
        y = 1.9 + k * 0.75
        shape(s, MSO_SHAPE.OVAL, LM, y, 0.55, 0.55, ORANGE if k in (2, 3) else BLUE, n, 17)
        text(s, LM + 0.8, y - 0.04, 7.0, 0.6, t, 19, INK, anchor=MSO_ANCHOR.MIDDLE)
    card(s, 8.55, 1.9, 4.03, 4.3, "Vocabulario", [Runs([B("Época: "), ("una pasada por todos los datos.", {})]),
                                                 Runs([B("Por lotes: "), ("una actualización por época con el promedio.", {})]),
                                                 Runs([B("Prueba: "), ("datos que no se usaron para entrenar.", {})])],
         BLUE, size=17, head_size=22)

    # 14 inicialización
    s = d.slide(notes="Ceros: todas las salidas iguales, hay que romper la simetría. Grandes: la sigmoide se satura. Xavier: "
                      "uniforme entre -1/raíz(n) y 1/raíz(n). n = 6 da ±0.408.")
    title(s, "Inicialización de los pesos")
    card(s, LM, 1.95, 3.8, 2.6, "¿Por qué no en cero?", "Todas las salidas serían iguales: hay que romper la simetría.",
         ORANGE, size=17, head_size=21)
    card(s, LM + 3.98, 1.95, 3.8, 2.6, "¿Por qué pequeños?", "Con pesos grandes la sigmoide se satura y aprende lento.",
         ORANGE, size=17, head_size=21)
    card(s, LM + 7.96, 1.95, 3.87, 2.6, "Xavier", [("w ~ U(−1/√n, +1/√n)", {"font": MONO, "color": INK}),
                                                   "n = número de entradas"], BLUE, size=17, head_size=21)
    rect(s, LM, 4.85, CW, 1.4, NAVY, radius=0.06)
    text(s, LM + 0.3, 4.85, CW - 0.6, 1.4, Runs([("Ejemplo: con n = 6 entradas, cada peso se elige al azar entre ", {}),
                                                 ("−0.408 y +0.408", {"bold": True, "color": AMBER})]), 21, CREAM,
         anchor=MSO_ANCHOR.MIDDLE)

    # 15 datos
    s = d.slide(notes="data_prep.py escala y separa 90% entrenamiento (360) y 10% prueba (40). La red dice admitido si ŷ > 0.5.")
    title(s, "Los datos de la práctica: admisiones")
    table(s, LM, 1.9, 7.0, [["Columna", "Qué es"], ["gre", "Puntaje del examen GRE (escalado)"], ["gpa", "Promedio (escalado)"],
                            ["rank_1 … rank_4", "Prestigio de la universidad de origen (0/1)"],
                            ["admit", "Salida: 1 admitido, 0 no"]], 17, [2.4, 4.6], 0.58)
    text(s, LM, 5.0, 7.0, 1.4, ["400 alumnos · 6 entradas", "90 % entrenamiento (360) · 10 % prueba (40)"], 17, GRAY, space=6)
    card(s, 8.1, 1.9, 4.48, 4.45, "Exactitud", [("aciertos / predicciones", {"font": MONO, "color": INK}),
                                                 Runs([("La red dice “admitido” si ", {}), B("ŷ > 0.5"), (".", {})]),
                                                 Runs([("Meta del notebook: ", {}), ("más de 0.74", {"bold": True, "color": ORANGE})])],
         BLUE, size=18, head_size=22)

    s = practica(d, "1_07_descenso_por_gradiente", "notebooks · 25 min · 3 puntos",
                 [("TODO 1 pt", "pesos con Xavier (np.random.uniform)"), ("TODO 1 pt", "completar el ciclo de entrenamiento"),
                  ("1 pt", "épocas hasta exactitud > 0.74")],
                 "# referencia (semilla 42, learnrate 0.5)\n# épocas  pérdida  exactitud\n#   10     0.225    0.60\n#  100     0.205    0.775\n# 1000     0.197    0.725",
                 "Pista: sigue los pasos 3 y 4 del algoritmo (diapositiva 13).",
                 "Con 1000 épocas la exactitud baja: primera probada de sobreajuste.", size=17)
    rect(s, LM, 5.2, CW, 1.25, RGBColor(0x22, 0x34, 0x5C), radius=0.06)
    text(s, LM + 0.3, 5.2, CW - 0.6, 1.25, Runs([("Usa ", {}), ("weights += …", {"font": MONO, "bold": True, "color": AMBER}),
                                                 (" y no weights = weights + …: la neurona comparte el arreglo; si creas uno "
                                                  "nuevo, la pérdida no baja.", {})]), 17, CREAM, anchor=MSO_ANCHOR.MIDDLE)

    # 17 ADALINE
    s = d.slide(notes="Activación lineal: regresión. f'(h) = 1. En 1_08 los datos no están escalados: la recta se ve bien pero "
                      "no es la óptima; escalando se llega a 9450·años + 24848.")
    title(s, "ADALINE: regresión con una neurona")
    try:
        import numpy as np
        dat = np.genfromtxt(os.path.join(os.path.dirname(__file__), "..", "notebooks", "files", "Salary_dataset.csv"),
                            delimiter=",", skip_header=1)
        xs_, ys_ = dat[:, 1], dat[:, 2] / 1000
    except Exception:          # sin datos, la gráfica queda solo con la recta
        xs_, ys_ = [], []
    g = plotbox(s, LM, 1.9, 6.4, 4.5, (0, 11.5), (0, 135), xlabel="años de experiencia", ylabel="salario (miles)")
    for a, b_ in zip(xs_, ys_):
        dot(s, g, a, b_, BLUE, 0.07)
    curve(s, g, lambda a: 9.45 * a + 24.848, (0.5, 11.2), (0, 135), ORANGE, 3.5)
    text(s, 7.4, 1.9, 5.18, 2.0, [Runs([B("Activación lineal: "), ("ŷ = w·x + b", {"font": MONO})]),
                                  Runs([B("Derivada: "), ("f′(h) = 1", {"font": MONO})]),
                                  Runs([B("Regla: "), ("w ← w + η(y − ŷ)x", {"font": MONO})])], 18, GRAY, space=8)
    rect(s, 7.4, 4.0, 5.18, 2.4, NAVY, radius=0.06)
    text(s, 7.65, 4.1, 4.7, 2.2, [("salario ≈ 9 450 · años + 24 848", {"bold": True, "color": AMBER}),
                                  "5 años → ≈ 72 098",
                                  ("Lección: escalar los datos acelera mucho el entrenamiento.", {"color": SOFT})], 17, CREAM,
         space=8)

    # 18 varias salidas
    s = d.slide(notes="Capa completamente conectada: cada entrada con cada salida. W es m x n, un sesgo por salida. La "
                      "activación se aplica elemento por elemento.")
    title(s, "Red de una capa con varias salidas")
    ins, outs = [(1.4, 2.6), (1.4, 4.8)], [(5.4, 2.6), (5.4, 4.8)]
    for i, (x, y) in enumerate(ins):
        for j, (x2, y2) in enumerate(outs):
            arrow(s, x + 0.4, y, x2 - 0.45, y2, GRAY, 2)
    for i, (x, y) in enumerate(ins):
        shape(s, MSO_SHAPE.OVAL, x - 0.4, y - 0.4, 0.8, 0.8, BLUE, f"x{'₁₂'[i]}", 20)
    for j, (x, y) in enumerate(outs):
        shape(s, MSO_SHAPE.OVAL, x - 0.45, y - 0.45, 0.9, 0.9, NAVY, f"ŷ{'₁₂'[j]}", 20)
    for lab, (x, y) in [("w₁₁", (3.0, 2.25)), ("w₂₂", (3.0, 4.95)), ("w₁₂", (2.35, 3.15)), ("w₂₁", (2.35, 3.85))]:
        text(s, x, y, 0.8, 0.4, lab, 15, ORANGE, True)
    text(s, LM, 5.75, 6.0, 0.6, "Cada entrada se conecta con cada salida: “completamente conectada”.", 15, GRAY)
    rect(s, 7.0, 1.95, 5.58, 1.3, NAVY, radius=0.06)
    text(s, 7.0, 1.95, 5.58, 1.3, "H = X·W + B     Ŷ = f(H)", 26, CREAM, True, MONO, align=PP_ALIGN.CENTER,
         anchor=MSO_ANCHOR.MIDDLE)
    text(s, 7.0, 3.5, 5.58, 2.9, [Runs([B("W: "), ("matriz de m entradas × n salidas.", {})]),
                                  Runs([B("B: "), ("un sesgo por salida.", {})]),
                                  Runs([B("f: "), ("se aplica a cada elemento de H.", {})]),
                                  Runs([B("Parámetros: "), ("(m + 1) · n", {"font": MONO})])], 18, GRAY, space=10)

    # 19 ejemplo varias salidas
    s = d.slide(notes="El libro trae H = [-7.7, 6.3] y ŷ = [4.52e-4, 0.981]; las cuentas correctas son -4.7 y 6.3. Úsalo como "
                      "reto: encuentren el error del libro.")
    title(s, "Ejemplo: 2 entradas, 2 salidas")
    text(s, LM, 1.8, CW, 0.5, "X = [8, 4] · W = [[−0.1, 0.6], [−0.8, 0.3]] · B = [−0.7, 0.3] · sigmoide", 17, GRAY, font=MONO)
    table(s, LM, 2.4, CW, [["Salida", "Combinación lineal", "Sigmoide"],
                           ["ŷ₁", "8·(−0.1) + 4·(−0.8) − 0.7 = −4.7", "σ(−4.7) ≈ 0.0090"],
                           ["ŷ₂", "8·0.6 + 4·0.3 + 0.3 = 6.3", "σ(6.3) ≈ 0.9982"]], 19, [1.4, 6.4, 4.03], 0.65)
    text(s, LM, 4.55, 6.0, 0.6, Runs([B("Parámetros: "), ("(2 + 1) · 2 = 6", {"font": MONO})]), 19, GRAY)
    rect(s, LM, 5.2, CW, 1.2, PALEORANGE, radius=0.06)
    text(s, LM + 0.3, 5.2, CW - 0.6, 1.2, Runs([("Reto: ", {"bold": True, "color": ORANGE}),
                                                ("el libro dice H = [−7.7, 6.3]. ¿Dónde está el error?", {})]), 19, INK,
         anchor=MSO_ANCHOR.MIDDLE)

    # 20 quiz
    s = d.slide(notes="Respuestas: 1) para que no se cancelen y castigar los grandes. 2) término de error, incremento, "
                      "actualización. 3) f'(h). 4) romper la simetría. 5) (3+1)·2 = 8.")
    s.background.fill.fore_color.rgb = ORANGE
    s._dark = True
    s._footer = WHITE
    title(s, "Quiz · 5 minutos")
    qs = ["¿Por qué el error se eleva al cuadrado?", "¿Cuáles son los tres pasos de la regla delta?",
          "¿Qué añade la regla delta respecto a la del perceptrón?", "¿Por qué no se inicializan los pesos en cero?",
          "¿Cuántos parámetros tiene una capa con 3 entradas y 2 salidas?"]
    text(s, LM, 1.95, CW, 4.6, [Runs([(f"{k + 1}.  ", {"bold": True, "color": NAVY}), (q, {})]) for k, q in enumerate(qs)],
         24, WHITE, space=16)

    cierre(d, ["Entrenar = bajar por el error moviendo los pesos.", "Regla delta: δ = (y − ŷ)·f′(h),  Δw = η·δ·x.",
               "Una sola capa sigue sin resolver XOR."],
           "Próximo módulo: redes multicapa y retropropagación.",
           "notebooks 1_06 y 1_07 (6 pts)", "libro, “Redes neuronales multicapa”",
           "Demo final: python docs/practica_04.py --graficar. OR se aprende; XOR se queda en 0.25.")
    return d


# ---------------------------------------------------------------- helpers clases 5–7
def repaso(d, titulo, tarjetas, hoy, notes="Pregunta antes de revelar cada tarjeta."):
    s = d.slide(notes=notes)
    title(s, titulo)
    for k, (h, b) in enumerate(tarjetas):
        card(s, LM + k * 3.98, 1.95, 3.8, 2.6, h, b, BLUE, size=19, head_size=21)
    text(s, LM, 5.0, CW, 1.0, hoy, 24, ORANGE, True)


def quiz(d, qs, notes):
    s = d.slide(notes=notes)
    s.background.fill.fore_color.rgb = ORANGE
    s._dark = True
    s._footer = WHITE
    title(s, "Quiz · 5 minutos")
    text(s, LM, 1.95, CW, 4.6, [Runs([(f"{k + 1}.  ", {"bold": True, "color": NAVY}), (q, {})]) for k, q in enumerate(qs)],
         22, WHITE, space=14)


def red(s, x0, y0, w, h, capas, nombres, color_capas=(BLUE, NAVY, ORANGE), r=0.28, linea=MUTED):
    """Dibuja una red completamente conectada. Devuelve las posiciones de los nodos por capa."""
    pos = []
    for c, n in enumerate(capas):
        x = x0 + c * (w / (len(capas) - 1))
        ys = [y0 + h / 2 + (k - (n - 1) / 2) * min(0.85, h / max(n, 1)) for k in range(n)]
        pos.append([(x, y) for y in ys])
    for c in range(len(capas) - 1):
        for (xa, ya) in pos[c]:
            for (xb, yb) in pos[c + 1]:
                arrow(s, xa + r, ya, xb - r, yb, linea, 1.3, head=False)
    for c, capa in enumerate(pos):
        col = color_capas[min(c, len(color_capas) - 1)]
        for (x, y) in capa:
            shape(s, MSO_SHAPE.OVAL, x - r, y - r, 2 * r, 2 * r, col)
        text(s, capa[0][0] - 1.0, y0 + h + 0.05, 2.0, 0.4, nombres[c], 15, INK, True, align=PP_ALIGN.CENTER)
    return pos


def grid(s, x0, y0, cell, M, size=16, fill=CARD, hl=None, hl_color=ORANGE, shade=False):
    """Dibuja una matriz de números como cuadrícula; hl = (fila0, col0, fila1, col1) se resalta."""
    for i, fila in enumerate(M):
        for j, v in enumerate(fila):
            f = fill
            if shade:
                g = int(255 - min(255, max(0, float(v))) * 0.75) if isinstance(v, (int, float)) else 245
                f = RGBColor(g, g, g)
            c = INK if not shade or (isinstance(v, (int, float)) and v < 150) else CREAM
            shp = shape(s, MSO_SHAPE.RECTANGLE, x0 + j * cell, y0 + i * cell, cell, cell, f, str(v), size, c, False,
                        line=BORDER, lw=1)
    if hl:
        r0, c0, r1, c1 = hl
        b = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x0 + c0 * cell), Inches(y0 + r0 * cell),
                               Inches((c1 - c0 + 1) * cell), Inches((r1 - r0 + 1) * cell))
        b.fill.background()
        b.line.color.rgb = hl_color
        b.line.width = Pt(4)
        b.shadow.inherit = False


# ================================================================ CLASE 5
def clase5():
    d = Deck("Introducción a las Redes Neuronales  ·  Clase 5")
    cover(d, "CLASE 5  ·  MÓDULO 4", "Redes multicapa y", "retropropagación",
          "Capas ocultas, pase hacia adelante, retropropagación… ¡y XOR resuelto!",
          "Hoy resolvemos el problema que quedó pendiente desde la clase 2: XOR.")
    agenda(d, [["0:00", "Repaso de la Clase 4"], ["0:10", "¿Por qué capas ocultas?"],
               ["0:25", "Pesos como matrices y pase hacia adelante"], ["0:45", "Práctica: 1_09"], ["1:05", "Descanso"],
               ["1:15", "Retropropagación"], ["1:45", "Práctica: 1_10"], ["2:00", "Entrenar la red completa y resolver XOR"],
               ["2:20", "Quiz y cierre"]], highlight=[5])
    objetivos(d, [("Explicar", "por qué una capa oculta resuelve XOR."), ("Calcular", "el pase hacia adelante con matrices."),
                  ("Aplicar", "un paso de retropropagación a mano."), ("Entrenar", "una red multicapa en Python.")])
    repaso(d, "Repaso de la Clase 4", [("¿Regla delta?", "Término de error, incremento y actualización."),
                                       ("¿Varias salidas?", "H = X·W + B: una matriz de pesos."),
                                       ("¿Qué quedó pendiente?", "XOR: una neurona solo traza una recta.")],
           "Hoy: juntar neuronas en capas para resolver XOR.")

    # 5 dos rectas
    s = d.slide(notes="Recta A deja abajo solo (0,0) (como OR); recta B deja arriba solo (1,1) (como AND). Los unos quedan "
                      "entre las dos rectas. Dos neuronas ocultas trazan las rectas y la salida las combina.")
    title(s, "XOR con dos rectas", "¿Por qué capas ocultas?")
    x0, y0, size = LM, 1.85, 4.4
    rect(s, x0, y0, size, size, CARD, BORDER, radius=0.03)
    m = 0.6
    g = lambda a, b: (x0 + m + a * (size - 2 * m), y0 + size - m - b * (size - 2 * m))  # noqa: E731
    polyline(s, [g(-0.15, 0.65), g(0.65, -0.15)], BLUE, 3.5)
    polyline(s, [g(0.35, 1.15), g(1.15, 0.35)], ORANGE, 3.5)
    for (a, b_), cls in [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 0)]:
        px, py = g(a, b_)
        if cls:
            shape(s, MSO_SHAPE.RECTANGLE, px - 0.17, py - 0.17, 0.34, 0.34, ORANGE)
        else:
            shape(s, MSO_SHAPE.OVAL, px - 0.17, py - 0.17, 0.34, 0.34, BLUE)
    text(s, x0, y0 + size + 0.05, size, 0.4, Runs([C("━ recta A   ", BLUE), C("━ recta B", ORANGE)]), 15, GRAY,
         align=PP_ALIGN.CENTER)
    text(s, 5.6, 1.9, 6.98, 4.6, [Runs([B("Neurona oculta 1: "), ("recta A (deja abajo solo el (0, 0)).", {})]),
                                  Runs([B("Neurona oculta 2: "), ("recta B (deja arriba solo el (1, 1)).", {})]),
                                  Runs([B("Neurona de salida: "), ("“arriba de A y debajo de B”.", {})]),
                                  ("Cada neurona oculta traza una recta; la salida las combina en una franja.",
                                   {"bold": True, "color": ORANGE})], 19, GRAY, space=14)

    # 6 arquitectura
    s = d.slide(notes="Capa de entrada (no calcula), oculta (no vemos su salida), salida. Perceptrón multicapa = MLP. Con "
                      "muchas capas ocultas: aprendizaje profundo.")
    title(s, "Perceptrón multicapa (MLP)")
    red(s, 1.5, 2.0, 5.0, 3.6, [4, 3, 2], ["Entrada (4)", "Oculta (3)", "Salida (2)"])
    text(s, 8.0, 2.0, 4.58, 4.4, [Runs([B("Entrada: "), ("los datos; no calcula nada.", {})]),
                                  Runs([B("Oculta: "), ("su salida no se ve desde afuera.", {})]),
                                  Runs([B("Salida: "), ("la predicción.", {})]),
                                  ("Muchas capas ocultas = aprendizaje profundo.", {"bold": True, "color": ORANGE})],
         19, GRAY, space=14)

    # 7 matrices
    s = d.slide(notes="Filas = entradas, columnas = neuronas de la capa siguiente. Regla de tamaños: el número del medio "
                      "debe coincidir.")
    title(s, "Los pesos son matrices")
    table(s, LM, 1.95, 6.6, [["Matriz", "Conecta", "Tamaño"], ["W₁", "entrada (4) → oculta (3)", "4 × 3"],
                             ["W₂", "oculta (3) → salida (2)", "3 × 2"], ["B₁", "un sesgo por neurona oculta", "1 × 3"],
                             ["B₂", "un sesgo por neurona de salida", "1 × 2"]], 18, [1.3, 3.8, 1.5], 0.62)
    rect(s, 7.6, 1.95, 4.98, 2.0, NAVY, radius=0.06)
    text(s, 7.6, 1.95, 4.98, 2.0, ["(a × b) · (b × c) = (a × c)", ("el número del medio debe coincidir", {"size": 16,
                                                                                                        "bold": False,
                                                                                                        "color": SOFT})],
         22, CREAM, True, MONO, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 7.6, 4.2, 4.98, 2.2, ["Ejemplo:", ("(1 × 4) · (4 × 3) = (1 × 3)", {"font": MONO, "bold": True, "color": INK}),
                                  "una fila de 3 números: las 3 neuronas ocultas."], 18, GRAY, space=8)

    # 8 pase adelante
    s = d.slide(notes="Es la clase 4 dos veces. La salida de una capa es la entrada de la siguiente.")
    title(s, "Pase hacia adelante")
    for k, (lab, f1, f2, sz) in enumerate([("Capa oculta", "H₁ = X·W₁ + B₁", "A₁ = σ(H₁)", "1 × 3"),
                                           ("Capa de salida", "H₂ = A₁·W₂ + B₂", "Ŷ = σ(H₂)", "1 × 2")]):
        x = LM + k * 6.0
        card(s, x, 1.95, 5.8, 3.0, lab, [(f1, {"font": MONO, "color": INK, "size": 24}), (f2, {"font": MONO, "color": INK,
                                                                                            "size": 24}),
                                         ("tamaño: " + sz, {"color": GRAY})], BLUE if k == 0 else ORANGE, size=18)
    arrow(s, LM + 5.8, 3.45, LM + 6.0, 3.45, GRAY, 3)
    text(s, LM, 5.3, CW, 1.0, "La salida de una capa (A₁) es la entrada de la siguiente.", 22, ORANGE, True)

    # 9 parámetros
    s = d.slide(notes="Por capa: (entradas + 1) por neuronas. 4-3-2: 15 + 8 = 23.")
    title(s, "Contar parámetros")
    table(s, LM, 1.95, 7.0, [["Capa", "Pesos", "Sesgos", "Total"], ["4 → 3", "4·3 = 12", "3", "15"], ["3 → 2", "3·2 = 6", "2", "8"],
                             [[("Red 4 → 3 → 2", {"bold": True})], "18", "5", [("23", {"bold": True, "color": ORANGE})]]],
          20, [2.5, 1.9, 1.3, 1.3], 0.7, align=[None] + [PP_ALIGN.CENTER] * 3, highlight=[3])
    rect(s, 8.1, 1.95, 4.48, 3.0, NAVY, radius=0.06)
    text(s, 8.35, 1.95, 4.0, 3.0, ["Regla por capa:", ("(entradas + 1) × neuronas", {"font": MONO, "color": AMBER})], 22,
         CREAM, True, anchor=MSO_ANCHOR.MIDDLE, space=10)

    practica(d, "1_09_red_multicapa_ejercicio", "notebooks · 20 min · 3 puntos",
             [("TODO 1 pt", "tamaños 4, 3, 2 y matrices W_1, W_2 con np.random.normal"),
              ("TODO 1 pt", "pase hacia adelante con np.dot"), ("1 pt", "agregar sesgos B_1 (1×3) y B_2 (1×2)")],
             "# comprobaciones\nW_1: (4, 3)  W_2: (3, 2)  X: (1, 4)\noculta: 3 números entre 0 y 1\nsalida: 2 números entre 0 y 1\nparámetros con sesgos: 23",
             "Pista: la segunda capa usa A_1 (después de la sigmoide), no H_1. Desviación sugerida: 1/√4.",
             "Diapositivas 7 a 9.")
    descanso(d, "la retropropagación")

    # 12 idea retro
    s = d.slide(notes="Con una neurona sabíamos el error. ¿Y una oculta? Se calcula el error en la salida y se manda hacia "
                      "atrás, repartido según los pesos. Analogía: repartir la responsabilidad de un partido perdido.")
    title(s, "¿Cuál es el error de una neurona oculta?", "Retropropagación")
    pos = red(s, 1.4, 2.0, 5.2, 3.4, [3, 2, 1], ["Entrada", "Oculta", "Salida"])
    (xo, yo) = pos[2][0]
    for (xh, yh) in pos[1]:
        arrow(s, xo - 0.32, yo + 0.12, xh + 0.32, yh + 0.12, ORANGE, 3, dash=True)
    text(s, xo - 0.6, yo - 0.85, 1.5, 0.4, "error", 16, ORANGE, True, align=PP_ALIGN.CENTER)
    text(s, 7.7, 1.95, 4.88, 4.4, ["Nadie nos dice qué debió producir una neurona oculta.",
                                   Runs([B("Solución: "), ("calcular el error en la salida y ", {}),
                                         ("mandarlo hacia atrás", {"bold": True, "color": ORANGE}), (".", {})]),
                                   "Cada neurona oculta recibe una parte según el peso que la une con la salida."],
         19, GRAY, space=14)

    # 13 fórmulas
    s = d.slide(notes="Con sigmoide f' = salida·(1 - salida). La oculta usa la misma regla delta, con error = δo · peso. Viene "
                      "de la regla de la cadena con un eslabón más.")
    title(s, "Las fórmulas")
    table(s, LM, 1.95, CW, [["Capa", "Término de error", "Incremento de sus pesos"],
                            ["Salida", "δₒ = (y − ŷ) · ŷ(1 − ŷ)", "Δw_ho = η · δₒ · a_h"],
                            ["Oculta", "δ_h = δₒ · w_ho · a_h(1 − a_h)", "Δw_ih = η · δ_h · xᵢ"]], 22, [2.0, 5.2, 4.63], 0.85)
    text(s, LM, 4.85, CW, 1.5, [Runs([B("a_h "), ("= salida de la neurona oculta.", {})]),
                                Runs([("La oculta usa la regla delta, pero su “error” es ", {}),
                                      ("δₒ × el peso que la une con la salida", {"bold": True, "color": ORANGE}), (".", {})])],
         19, GRAY, space=8)

    # 14 ejemplo adelante
    s = d.slide(notes="Red 3-2-1 del notebook 1_10. Hazlo en el pizarrón.")
    title(s, "Ejemplo (notebook 1_10): hacia adelante")
    text(s, LM, 1.8, CW, 0.5, "x = [0.5, 0.1, −0.2] · y = 0.6 · η = 0.5 · W_ih = [[0.5, −0.6], [0.1, −0.2], [0.1, 0.7]] · "
                               "W_ho = [0.1, −0.3]", 15, GRAY, font=MONO)
    table(s, LM, 2.45, CW, [["Valor", "Cálculo", "Resultado"], ["Entrada a la oculta", "x · W_ih", "[0.24, −0.46]"],
                            ["Salida oculta a_h", "σ(…)", "[0.5597, 0.3870]"],
                            ["Entrada a la salida", "0.5597·0.1 + 0.3870·(−0.3)", "−0.0601"],
                            ["Salida ŷ", "σ(−0.0601)", [("0.4850", {"bold": True, "color": ORANGE})]]], 19, [3.3, 5.0, 3.53],
          0.66, highlight=[4])

    # 15 ejemplo atrás
    s = d.slide(notes="Los incrementos tienen el mismo tamaño que los pesos. Con otra η se escalan igual.")
    title(s, "Ejemplo (notebook 1_10): hacia atrás")
    table(s, LM, 1.9, CW, [["Valor", "Cálculo", "Resultado"], ["Error", "0.6 − 0.4850", "0.1150"],
                           ["δₒ", "0.1150 · 0.4850 · 0.5150", "0.02873"],
                           ["δ_h", "0.02873 · [0.1, −0.3] · a_h(1 − a_h)", "[0.000708, −0.002045]"],
                           ["Δw_ho", "0.5 · 0.02873 · [0.5597, 0.3870]", "[0.00804, 0.00556]"],
                           ["Δw_ih", "0.5 · δ_h · x  (matriz 3 × 2)", "[[0.000177, −0.000511], …]"]], 18, [1.8, 5.6, 4.43], 0.62)
    text(s, LM, 5.85, CW, 0.6, "Cada peso tiene su incremento: las matrices de incrementos miden lo mismo que las de pesos.",
         18, ORANGE, True)

    # 16 desvanece
    s = d.slide(notes="El error llega multiplicado por pesos pequeños y derivadas de la sigmoide (máx. 0.25). Con muchas capas "
                      "casi desaparece. Por eso las redes profundas usan ReLU.")
    title(s, "El gradiente que se desvanece")
    for k, (lab, val, col) in enumerate([("|δ| salida", 0.02873, ORANGE), ("|δ| oculta (mayor)", 0.002045, BLUE)]):
        hbar = 4.2 * val / 0.02873
        x = LM + 0.6 + k * 2.6
        rect(s, x, 6.2 - hbar, 1.6, hbar, col, rounded=False)
        text(s, x - 0.3, 6.25, 2.2, 0.4, lab, 15, INK, True, align=PP_ALIGN.CENTER)
        text(s, x - 0.3, 6.2 - hbar - 0.45, 2.2, 0.4, f"{val:.5f}", 15, col, True, align=PP_ALIGN.CENTER)
    text(s, 6.6, 1.95, 5.98, 4.4, [("La capa oculta recibe un error ~14 veces más pequeño.", {"bold": True, "color": INK}),
                                   "Se multiplica por pesos pequeños y por derivadas de la sigmoide (≤ 0.25).",
                                   "Con muchas capas, las primeras casi no aprenden.",
                                   ("Por eso las redes profundas usan ReLU.", {"bold": True, "color": ORANGE})],
         19, GRAY, space=14)

    practica(d, "1_10_retropropagacion_base", "notebooks · 15 min · 3 puntos",
             [("TODO 1 pt", "error, δ de salida y δ de la oculta"), ("TODO 1 pt", "incrementos y actualización"),
              ("1 pt", "¿mismo tamaño que los pesos?")],
             "# comprobaciones (η = 0.5)\nerror = 0.1150\ndelta salida = 0.02873\ndelta oculta = [0.000708 -0.002045]\nΔw_ho = [0.00804 0.00556]",
             "Pista: para Δw_ih convierte x en columna con x[:, None]: da una matriz 3 × 2.", "Diapositivas 13 a 15.")

    # 18 algoritmo + 1_11
    s = d.slide(notes="Notebook 1_11: datos de admisiones, red 6-2-1, 900 épocas, semilla 21. El original imprime la pérdida "
                      "con solo el último ejemplo: usar features.values.")
    title(s, "Entrenar la red completa (notebook 1_11)")
    pasos = ["Incrementos acumulados = 0", "Por ejemplo: adelante → δₒ y δ_h → acumular", "Actualizar W_ih y W_ho",
             "Medir la pérdida y repetir"]
    for k, t in enumerate(pasos):
        y = 1.95 + k * 0.72
        shape(s, MSO_SHAPE.OVAL, LM, y, 0.52, 0.52, BLUE, str(k + 1), 16)
        text(s, LM + 0.75, y - 0.04, 5.0, 0.6, t, 17, INK, anchor=MSO_ANCHOR.MIDDLE)
    table(s, 6.5, 1.95, 6.08, [["Actualización", "Pérdida", "Exactitud"], ["0.001 · acumulado", "0.265 → 0.201", "0.725"],
                               ["0.5 · acum. / n", "0.264 → 0.200", [("0.750", {"bold": True, "color": ORANGE})]]],
          17, [2.5, 2.1, 1.48], 0.62)
    rect(s, LM, 5.15, CW, 1.2, PALEORANGE, radius=0.06)
    text(s, LM + 0.3, 5.15, CW - 0.6, 1.2, Runs([("Ojo: ", {"bold": True, "color": ORANGE}),
                                                 ("el notebook original imprime la pérdida con solo el último ejemplo (x). "
                                                  "Usa features.values.", {})]), 18, INK, anchor=MSO_ANCHOR.MIDDLE)

    practica(d, "1_11 + ¡XOR resuelto!", "notebooks · 20 min · 3 puntos  ·  + docs/practica_05.py",
             [("TODO 1 pt", "ciclo de entrenamiento"), ("TODO 1 pt", "curva de aprendizaje"), ("1 pt", "preguntas")],
             "# python docs/practica_05.py  (red 2-3-1)\n[0 0] -> 0.025 -> 0\n[0 1] -> 0.981 -> 1\n[1 0] -> 0.971 -> 1\n[1 1] -> 0.026 -> 0\npérdida: 0.2596 -> 0.0006",
             "Demo: python docs/practica_05.py --graficar. La frontera aprendida ya no es una recta.",
             "Cierra con XOR resuelto en vivo.")
    quiz(d, ["¿Por qué una capa oculta permite resolver XOR?", "¿Qué tamaño tiene W entre una capa de 4 y una de 3?",
             "¿Cuántos parámetros tiene una red 2 → 3 → 1?", "¿Cómo se calcula el error de una neurona oculta?",
             "¿Qué es el gradiente que se desvanece?"],
         "Respuestas: 1) cada oculta traza una recta y la salida las combina. 2) 4 × 3. 3) 13. 4) δo · peso · derivada. "
         "5) el error se hace muy pequeño al ir hacia atrás.")
    cierre(d, ["Las capas ocultas combinan rectas: resuelven problemas no lineales.",
               "Pase hacia adelante: la clase 4 repetida capa por capa.",
               "Retropropagación: el error viaja hacia atrás, repartido según los pesos."],
           "Próxima clase: optimizadores (cómo caminar mejor por la montaña del error).",
           "notebooks 1_09, 1_10 y 1_11 (9 pts)", "libro, “Retropropagación”",
           "Tarea extra: en practica_05.py cambiar n_ocultas a 2 y 8, y la semilla.")
    return d


# ================================================================ CLASE 6
def clase6():
    d = Deck("Introducción a las Redes Neuronales  ·  Clase 6")
    cover(d, "CLASE 6  ·  OPTIMIZACIÓN", "Optimizadores:", "caminar mejor",
          "Descenso por gradiente en 2D, momentum y decaimiento de la tasa de aprendizaje",
          "Entrenar es bajar por la montaña del error; el optimizador es la forma de caminar.")
    agenda(d, [["0:00", "Repaso"], ["0:10", "Descenso por gradiente en 2D"], ["0:30", "Práctica: notebook 21"],
               ["0:45", "Valles estrechos y momentum"], ["1:10", "Práctica: notebook 22"], ["1:25", "Descanso"],
               ["1:35", "Decaimiento de la tasa"], ["2:00", "Práctica: notebook 23"], ["2:20", "Quiz y cierre"]], highlight=[6])
    objetivos(d, [("Aplicar", "el descenso con dos parámetros."), ("Leer", "un mapa de contorno."),
                  ("Explicar", "el momentum y cuándo ayuda."), ("Programar", "el decaimiento de la tasa.")])
    repaso(d, "Repaso", [("¿La regla?", "x ← x − η · f′(x)"), ("¿η muy grande?", "Oscila o diverge."),
                         ("¿η muy pequeña?", "Avanza muy lento.")],
           "Hoy: muchos parámetros y montañas con formas difíciles.")

    # 5 derivadas parciales
    s = d.slide(notes="Una derivada por variable, tratando la otra como número fijo. El gradiente apunta hacia donde sube más "
                      "rápido; bajamos en contra.")
    title(s, "Descenso por gradiente en 2D")
    card(s, LM, 1.95, 5.8, 2.6, "Esfera: f(x, y) = x² + y²",
         [("∂f/∂x = 2x", {"font": MONO, "color": INK}), ("∂f/∂y = 2y", {"font": MONO, "color": INK}),
          "Una derivada por variable (la otra queda fija)."], BLUE, size=19, head_size=22)
    card(s, LM + 6.0, 1.95, 5.83, 2.6, "Gradiente ∇f = (2x, 2y)",
         ["Una flecha que apunta hacia donde f sube más rápido.", ("Bajamos en contra.", {"bold": True, "color": ORANGE})],
         ORANGE, size=19, head_size=22)
    rect(s, LM, 4.85, CW, 1.4, NAVY, radius=0.06)
    text(s, LM, 4.85, CW, 1.4, ["x ← x − η · ∂f/∂x", "y ← y − η · ∂f/∂y"], 24, CREAM, True, MONO, align=PP_ALIGN.CENTER,
         anchor=MSO_ANCHOR.MIDDLE, space=2)

    # 6 contorno
    s = d.slide(notes="Mapa topográfico: cada línea une puntos de igual altura. El camino cruza las líneas en ángulo recto.")
    title(s, "El mapa de contorno")
    cx, cy = LM + 3.0, 4.15
    for k, rr in enumerate([2.3, 1.75, 1.2, 0.65]):
        shape(s, MSO_SHAPE.OVAL, cx - rr, cy - rr, 2 * rr, 2 * rr, None, line=[NAVY, BLUE, LBLUE, AMBER][k], lw=2.5)
    pts = [(-1.0, -1.0), (-0.8, -0.8), (-0.55, -0.55), (-0.3, -0.3), (-0.1, -0.1)]
    sc = 1.6
    polyline(s, [(cx + a * sc, cy - b * sc) for a, b in pts], ORANGE, 3)
    for a, b in pts:
        shape(s, MSO_SHAPE.OVAL, cx + a * sc - 0.08, cy - b * sc - 0.08, 0.16, 0.16, ORANGE)
    shape(s, MSO_SHAPE.OVAL, cx - 0.12, cy - 0.12, 0.24, 0.24, NAVY)
    text(s, 7.2, 2.0, 5.38, 4.4, ["Como un mapa topográfico: cada línea une puntos de la misma “altura”.",
                                  "En la esfera son círculos alrededor del mínimo (0, 0).",
                                  ("El camino cruza las líneas en ángulo recto: el gradiente es perpendicular a ellas.",
                                   {"bold": True, "color": ORANGE})], 19, GRAY, space=14)

    # 7 tabla eta
    s = d.slide(notes="Cada paso multiplica x por (1 - 2η): 0.9 → -0.8 (zigzag que se achica), 1 → -1 (rebota), >1 diverge.")
    title(s, "El efecto de η en 2D (notebook 21)")
    table(s, LM, 1.9, CW, [["η", "Iteraciones", "Qué pasa"], ["0.01", "300", "Lento: termina en (−0.0023, −0.0023)"],
                           ["0.1", "56", "Bien"], ["0.5", "2", "De un salto (solo en esta función)"],
                           ["0.9", "66", "Llega zigzagueando"], ["1.0", "300", "Rebota para siempre entre (−1, −1) y (1, 1)"]],
          19, [1.6, 2.4, 7.83], 0.58, align=[PP_ALIGN.CENTER, PP_ALIGN.CENTER, None])
    text(s, LM, 5.6, CW, 0.8, Runs([("Cada paso multiplica x por ", {}), ("(1 − 2η)", {"font": MONO, "bold": True}),
                                    (": con η > 1 crece y diverge.", {})]), 19, GRAY)

    practica(d, "21_opt_gradiente_2d", "notebooks · 15 min · experimentos",
             [("1", "Ejecuta con los valores originales"), ("2", "Cambia learning_rate: 0.1, 0.5, 0.9, 1.0"),
              ("3", "Anota iteraciones y compáralas con la tabla")],
             "# valores originales\nParámetros: [-0.00233, -0.00233]\nValor: 1.09e-05\n\n# sin ffmpeg, la animación:\n.save('x.gif', writer='pillow')",
             "La clase GradientDescentOptimizer guarda cada paso en history: así se dibuja el camino.", "Diapositiva 7.")

    # 9 valle estrecho
    s = d.slide(notes="Función de Beale: valle largo, estrecho y curvo; mínimo en (3, 0.5). El gradiente apunta a las paredes, "
                      "no a lo largo del valle.")
    title(s, "Valles estrechos: la función de Beale", "Momentum")
    cx, cy = LM + 3.2, 4.1
    for k, (rw, rh) in enumerate([(3.0, 1.6), (2.3, 1.15), (1.6, 0.7), (0.9, 0.3)]):
        shape(s, MSO_SHAPE.OVAL, cx - rw, cy - rh, 2 * rw, 2 * rh, None, line=[NAVY, BLUE, LBLUE, AMBER][k], lw=2.5)
    zig = [(-2.6, 0.9), (-2.1, -0.75), (-1.6, 0.6), (-1.1, -0.5), (-0.6, 0.35), (-0.2, -0.2)]
    polyline(s, [(cx + a, cy + b) for a, b in zig], ORANGE, 3)
    shape(s, MSO_SHAPE.OVAL, cx - 0.12, cy - 0.12, 0.24, 0.24, NAVY)
    text(s, 7.4, 2.0, 5.18, 4.4, ["Valle largo, estrecho y curvo. Mínimo en (3, 0.5).",
                                  "El gradiente apunta casi siempre hacia las paredes.",
                                  ("Con η grande, el descenso rebota de pared a pared y puede salir disparado.",
                                   {"bold": True, "color": ORANGE})], 19, GRAY, space=14)

    # 10 momentum fórmula
    s = d.slide(notes="Promedio de los gradientes recientes. β es la memoria. Con β = 0 es el descenso simple.")
    title(s, "La idea del momentum")
    rect(s, LM, 1.95, CW, 1.5, NAVY, radius=0.06)
    text(s, LM, 1.95, CW, 1.5, ["m ← β · m + (1 − β) · ∇f", "parámetros ← parámetros − η · m"], 26, CREAM, True, MONO,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, space=2)
    card(s, LM, 3.75, 5.8, 2.6, "Promedio de gradientes", "En vez del gradiente de este instante, un promedio de los recientes.",
         BLUE, size=18, head_size=22)
    card(s, LM + 6.0, 3.75, 5.83, 2.6, "β = memoria", "Con β = 0.9 el paso de ahora se parece mucho a los anteriores.",
         ORANGE, size=18, head_size=22)

    # 11 bola
    s = d.slide(notes="Los empujones a los lados cambian de signo y se cancelan; el empuje a lo largo del valle se mantiene.")
    title(s, "Una bola rodando por el valle")
    text(s, LM, 1.95, 6.2, 3.0, ["Los empujones hacia las paredes cambian de signo en cada rebote: ",
                                 ("en el promedio se cancelan.", {"bold": True, "color": ORANGE}),
                                 "El empuje a lo largo del valle va siempre en la misma dirección: ",
                                 ("se mantiene.", {"bold": True, "color": BLUE})], 19, GRAY, space=4)
    table(s, 7.3, 1.95, 5.28, [["β", "Efecto"], ["0", "Sin memoria: descenso simple"], ["0.5 – 0.9", "Suaviza los rebotes"],
                               ["0.99", "Demasiada memoria: le cuesta girar"]], 17, [1.5, 3.78], 0.62)

    # 12 resultados momentum
    s = d.slide(notes="Conclusión honesta: con η pequeña no acelera (promedia); su ventaja es permitir η grande sin diverger.")
    title(s, "Resultados en Beale (notebook 22)")
    text(s, LM, 1.8, CW, 0.5, "Desde (2.5, 1.0), 500 iteraciones", 17, GRAY)
    table(s, LM, 2.35, CW, [["η", "Descenso simple", "Momentum β = 0.5", "Momentum β = 0.9"],
                            ["0.01", "f = 6.95·10⁻⁴", "f = 7.37·10⁻⁴", "f = 1.07·10⁻³"],
                            ["0.03", [("diverge", {"bold": True, "color": ORANGE})], "f = 1.9·10⁻⁶",
                             [("f = 8.0·10⁻⁷", {"bold": True, "color": BLUE})]]], 20, [1.5, 3.4, 3.4, 3.53], 0.75,
          align=[PP_ALIGN.CENTER] * 4, highlight=[2])
    rect(s, LM, 4.9, CW, 1.4, NAVY, radius=0.06)
    text(s, LM + 0.3, 4.9, CW - 0.6, 1.4, "El momentum permite usar una η más grande sin descontrolarse… y llega mucho más "
                                          "cerca del mínimo.", 20, CREAM, True, anchor=MSO_ANCHOR.MIDDLE)

    practica(d, "22_opt_momentum", "notebooks · 15 min · experimentos",
             [("1", "Ejecuta con los valores originales"), ("2", "Sube learning_rate a 0.03"),
              ("3", "Compara con el descenso simple (línea comentada)")],
             "# originales (η 0.01, β 0.9)\nfinal ≈ (2.922, 0.480)  f ≈ 1.07e-03\n\n# η 0.03\ndescenso simple: OverflowError\nmomentum: ≈ (2.998, 0.499)",
             "Crea un optimizador nuevo en cada prueba: el objeto recuerda su momentum.", "Diapositiva 12.")
    descanso(d, "el decaimiento de la tasa")

    # 15 dilema
    s = d.slide(notes="Fija grande: rápido pero rebota. Fija pequeña: fino pero lento. Solución: empezar grande y reducir.")
    title(s, "El dilema de la tasa fija", "Decaimiento de la tasa")
    for k, (h, b, c) in enumerate([("η grande", "Avanza rápido… pero cerca del mínimo rebota.", ORANGE),
                                   ("η pequeña", "Afina bien… pero tarda muchísimo.", BLUE),
                                   ("Decaimiento", "Empieza grande y la reduce con el tiempo.", NAVY)]):
        card(s, LM + k * 3.98, 1.95, 3.8, 3.0, h, b, c, size=19, head_size=24)
    text(s, LM, 5.3, CW, 1.0, "Lo mejor de los dos mundos: rápido al principio, fino al final.", 22, ORANGE, True)

    # 16 tres reglas + gráfica
    s = d.slide(notes="t es la iteración. Escalonada: a la mitad cada 100. Inversa: rápido al inicio, luego despacio. "
                      "Exponencial: suave pero puede bajar demasiado.")
    title(s, "Tres reglas de decaimiento")
    table(s, LM, 1.9, 6.4, [["Regla", "Fórmula"], ["Escalonada", "η₀ · γ^(t // s)"], ["Inversa", "η₀ / (1 + k·t)"],
                            ["Exponencial", "η₀ · e^(−k·t)"]], 19, [2.4, 4.0], 0.7)
    g = plotbox(s, 7.4, 1.9, 5.18, 4.45, (0, 500), (0, 0.055), xlabel="iteración t", ylabel="η")
    curve(s, g, lambda t: 0.05 * 0.5 ** (t // 100), (0, 500), (0, 0.055), ORANGE, 3, n=500)
    curve(s, g, lambda t: 0.05 / (1 + 0.01 * t), (0, 500), (0, 0.055), BLUE, 3)
    curve(s, g, lambda t: 0.05 * math.exp(-0.01 * t), (0, 500), (0, 0.055), NAVY, 3)
    text(s, LM, 5.0, 6.4, 1.3, Runs([C("━ escalonada  ", ORANGE), C("━ inversa  ", BLUE), C("━ exponencial", NAVY)]), 17, GRAY)

    # 17 valores
    s = d.slide(notes="Haz en el pizarrón la escalonada en t = 250: 250 // 100 = 2, 0.05 · 0.5² = 0.0125.")
    title(s, "Calcular a mano")
    text(s, LM, 1.8, CW, 0.5, "η₀ = 0.05 · γ = 0.5 cada s = 100 · k = 0.01", 18, GRAY, font=MONO)
    table(s, LM, 2.4, CW, [["t", "Escalonada", "Inversa", "Exponencial"], ["0", "0.05", "0.05", "0.05"],
                           ["100", "0.025", "0.025", "0.0184"], ["250", "0.0125", "0.0143", "0.0041"]], 22,
          [2.0, 3.3, 3.3, 3.23], 0.75, align=[PP_ALIGN.CENTER] * 4, highlight=[3])
    text(s, LM, 5.65, CW, 0.7, "Escalonada en t = 250:  250 // 100 = 2  →  0.05 · 0.5² = 0.0125", 19, ORANGE, True, MONO)

    # 18 resultados
    s = d.slide(notes="Escalonada: casi mil veces menos error que la fija. Exponencial con k = 0.01 decae muy rápido y se congela.")
    title(s, "Resultados en Beale (notebook 23)")
    text(s, LM, 1.8, CW, 0.5, "Desde (1.0, 1.0), η₀ = 0.05, 500 iteraciones", 17, GRAY)
    table(s, LM, 2.35, CW, [["Configuración", "f final", "Qué pasa"], ["Tasa fija 0.05", "5.8·10⁻²", "Rebota, no llega"],
                            ["Escalonada", "6.3·10⁻⁵", "Casi mil veces mejor"], ["Inversa", "1.0·10⁻⁴", "Muy bien"],
                            ["Exponencial", "1.5·10⁻³", "Decae demasiado rápido: se congela"],
                            ["Escalonada con γ = 0.8", [("7.8·10⁻⁷", {"bold": True, "color": BLUE})], "La mejor"]],
          19, [4.0, 2.6, 5.23], 0.6, highlight=[5])

    practica(d, "23_opt_lr_decay", "notebooks · 20 min · 3 puntos  ·  nuevo (el original estaba vacío)",
             [("TODO 1 pt", "las tres reglas de decaimiento"), ("TODO 1 pt", "next_params con la tasa de cada iteración"),
              ("TODO 1 pt", "experimentar y comparar")],
             "# comprobaciones\nt=100: 0.02500  0.02500  0.01839\nt=250: 0.01250  0.01429  0.00410\n\nfija 0.05:     f = 5.76e-02\ndecaimiento:   f = 6.34e-05",
             "Pista: guarda la tasa en self.tasas, súmale 1 a self.t y devuelve param − tasa · gradiente.",
             "Demo final: python docs/practica_06.py --graficar")
    quiz(d, ["¿Qué es el gradiente de f(x, y)?", "¿Por qué el descenso rebota en un valle estrecho?",
             "¿Qué controla β en el momentum?", "¿Qué ventaja dio el momentum en Beale?",
             "¿Qué pasa si la tasa decae demasiado rápido?"],
         "Respuestas: 1) vector de derivadas parciales, apunta hacia donde sube. 2) el gradiente apunta a las paredes. "
         "3) la memoria. 4) permitió η = 0.03 sin diverger. 5) se congela antes de llegar.")
    cierre(d, ["Más parámetros: mismo descenso, una derivada por parámetro.",
               "Momentum: suaviza rebotes y permite tasas más grandes.",
               "Decaimiento: empezar rápido y terminar fino."],
           "Próxima clase: redes convolucionales, el puente al aprendizaje profundo.",
           "notebook 23 (3 pts) + conclusiones de 21 y 22", "Goodfellow et al., Deep Learning, secciones 8.3 (momentum) y 8.5 (Adam)",
           "Adam combina momentum con una tasa que se adapta a cada parámetro.")
    return d


# ================================================================ CLASE 7
def clase7():
    d = Deck("Introducción a las Redes Neuronales  ·  Clase 7")
    cover(d, "CLASE 7  ·  PUENTE AL APRENDIZAJE PROFUNDO", "Redes", "convolucionales",
          "Imágenes, kernels, detección de bordes y cómo se aprende un filtro",
          "Hoy aplicamos todo lo aprendido a imágenes: la base de las redes profundas para visión.")
    agenda(d, [["0:00", "Repaso"], ["0:10", "Imágenes y por qué convolución"], ["0:25", "Correlación cruzada"],
               ["0:50", "Detector de bordes y ReLU"], ["1:00", "Práctica: 3_1"], ["1:30", "Descanso"],
               ["1:40", "Aprender el kernel"], ["2:05", "Reto: 3_2 y practica_07"], ["2:25", "Quiz y cierre"]], highlight=[6])
    objetivos(d, [("Explicar", "por qué se usan convoluciones en imágenes."), ("Calcular", "una correlación cruzada a mano."),
                  ("Programar", "la operación de una capa convolucional."),
                  ("Entrenar", "los números de un kernel con descenso.")])
    repaso(d, "Repaso", [("¿Una capa?", "H = X·W + B y una activación."), ("¿Cómo se entrena?", "Descenso por gradiente."),
                         ("¿Momentum?", "Suaviza rebotes y permite η grande.")],
           "Hoy: lo mismo, pero sobre imágenes.")

    # 5 imagen = matriz
    s = d.slide(notes="Escala de grises: 0 negro, 255 blanco. Color: 3 matrices (R, G, B). La foto de los notebooks mide 256 × 256.")
    title(s, "Una imagen es una matriz de números", "Imágenes")
    M = [[30, 60, 120, 200, 240, 250], [25, 55, 110, 190, 235, 245], [20, 50, 100, 180, 230, 240],
         [20, 45, 95, 170, 225, 235], [15, 40, 90, 160, 220, 230]]
    grid(s, LM, 2.0, 0.78, M, 14, shade=True)
    text(s, 6.0, 2.0, 6.58, 4.4, [Runs([B("Escala de grises: "), ("0 = negro, 255 = blanco.", {})]),
                                  Runs([B("A color: "), ("3 matrices (rojo, verde, azul).", {})]),
                                  Runs([B("La foto de los notebooks: "), ("256 × 256 = 65 536 números por canal.", {})])],
         19, GRAY, space=14)

    # 6 densa vs conv
    s = d.slide(notes="Con capas densas: 65 536 × 100 = 6.5 millones de pesos e ignora la vecindad. Convolución: 9 pesos que "
                      "recorren toda la imagen y buscan el mismo patrón en todas partes.")
    title(s, "¿Por qué no una capa densa?")
    card(s, LM, 1.95, 5.8, 3.6, "Capa densa", ["65 536 píxeles × 100 neuronas", ("= 6.5 millones de pesos",
                                                                              {"bold": True, "color": ORANGE}),
                                               "Ignora que los píxeles vecinos se relacionan."], ORANGE, size=19, head_size=24)
    card(s, LM + 6.0, 1.95, 5.83, 3.6, "Convolución", ["Un filtro de 3 × 3", ("= 9 pesos", {"bold": True, "color": BLUE}),
                                                       "Los mismos pesos recorren toda la imagen: buscan el mismo patrón en "
                                                       "todas partes."], BLUE, size=19, head_size=24)
    text(s, LM, 5.85, CW, 0.6, "Un gato en la esquina o en el centro: el mismo filtro lo detecta.", 19, GRAY)

    # 7 kernel deslizante
    s = d.slide(notes="Coloca el kernel, multiplica cada número por el píxel de abajo, suma todo: un píxel de salida. Desliza y "
                      "repite.")
    title(s, "El kernel se desliza sobre la imagen", "Correlación cruzada")
    I5 = [[0, 0, 9, 9, 9]] * 5
    grid(s, LM, 2.0, 0.62, I5, 16, hl=(0, 0, 2, 2))
    text(s, LM, 5.2, 3.1, 0.4, "Imagen 5 × 5", 15, INK, True, align=PP_ALIGN.CENTER)
    text(s, 4.15, 3.25, 0.6, 0.5, "⊗", 28, GRAY, True, align=PP_ALIGN.CENTER)
    grid(s, 4.85, 2.6, 0.62, [[-1, 0, 1]] * 3, 16, fill=PALEORANGE)
    text(s, 4.6, 4.55, 2.4, 0.4, "Kernel 3 × 3", 15, INK, True, align=PP_ALIGN.CENTER)
    arrow(s, 6.85, 3.5, 7.45, 3.5, GRAY, 3)
    grid(s, 7.6, 2.6, 0.62, [[27, 27, 0]] * 3, 16, hl=(0, 0, 0, 0), hl_color=BLUE)
    text(s, 7.35, 4.55, 2.4, 0.4, "Salida 3 × 3", 15, INK, True, align=PP_ALIGN.CENTER)
    text(s, 9.8, 2.0, 2.78, 4.3, ["1. Coloca el kernel.", "2. Multiplica cada número por el píxel de abajo.",
                                  "3. Suma todo: un píxel de salida.", "4. Desliza y repite."], 16, GRAY, space=10)

    # 8 ejemplo
    s = d.slide(notes="Fila 0 0 9 9 9 y kernel -1 0 1: cada fila aporta 9, tres filas = 27. En zona plana: 0. El kernel se "
                      "enciende donde hay un borde vertical.")
    title(s, "Ejemplo en el pizarrón")
    text(s, LM, 1.8, CW, 0.5, "Cada fila de la imagen: 0 0 9 9 9   ·   cada fila del kernel: −1 0 1", 18, GRAY, font=MONO)
    table(s, LM, 2.45, CW, [["Ventana (columnas)", "Valores", "Cálculo por fila", "× 3 filas"],
                            ["0 – 2", "0 0 9", "−0 + 0 + 9 = 9", "27"], ["1 – 3", "0 9 9", "−0 + 0 + 9 = 9", "27"],
                            ["2 – 4", "9 9 9", "−9 + 0 + 9 = 0", "0  (zona plana)"]], 19, [3.0, 2.3, 3.6, 2.93], 0.66,
          align=[PP_ALIGN.CENTER] * 4)
    text(s, LM, 5.3, CW, 1.0, [Runs([B("Salida: "), ("[[27, 27, 0], [27, 27, 0], [27, 27, 0]]", {"font": MONO})]),
                               ("El kernel se enciende donde hay un borde vertical y vale 0 donde la imagen es plana.",
                                {"bold": True, "color": ORANGE})], 18, GRAY, space=6)

    # 9 tamaño
    s = d.slide(notes="Sin padding la salida pierde k píxeles por lado: n - 2k. Con padding de ceros puede medir lo mismo.")
    title(s, "Tamaño de la salida")
    rect(s, LM, 1.95, CW, 1.2, NAVY, radius=0.06)
    text(s, LM, 1.95, CW, 1.2, "sin padding:  salida = n − 2k", 28, CREAM, True, MONO, align=PP_ALIGN.CENTER,
         anchor=MSO_ANCHOR.MIDDLE)
    table(s, LM, 3.45, CW, [["Imagen", "Kernel", "k", "Salida"], ["5 × 5", "3 × 3", "1", "3 × 3"],
                            ["256 × 256", "3 × 3", "1", "254 × 254"], ["256 × 256", "5 × 5", "2", "252 × 252"]], 19,
          [3.2, 2.8, 1.6, 4.23], 0.58, align=[PP_ALIGN.CENTER] * 4)
    text(s, LM, 5.95, CW, 0.5, "Con padding (rellenar la orilla con ceros) la salida puede medir lo mismo que la entrada.", 17,
         GRAY)

    # 10 kernel del notebook
    s = d.slide(notes="Es el ejemplo dividido entre 3. Positivo de oscuro a claro, negativo de claro a oscuro, cero en lo plano.")
    title(s, "El kernel del notebook 3_1", "Detector de bordes y ReLU")
    grid(s, LM + 0.3, 2.1, 1.05, [["−1/3", "0", "1/3"]] * 3, 17, fill=PALEORANGE)
    text(s, 5.0, 2.0, 7.58, 4.4, [Runs([("Positivo ", {"bold": True, "color": BLUE}),
                                        ("donde la imagen pasa de oscuro a claro (→).", {})]),
                                  Runs([("Negativo ", {"bold": True, "color": ORANGE}),
                                        ("donde pasa de claro a oscuro.", {})]),
                                  Runs([B("≈ 0 "), ("en zonas planas.", {})])], 20, GRAY, space=16)

    # 11 relu
    s = d.slide(notes="Respuesta a la pregunta del notebook: la ReLU borra los negativos (bordes claro→oscuro) y el kernel no ve "
                      "bordes horizontales.")
    title(s, "¿Por qué solo se ven algunos bordes?")
    card(s, LM, 1.95, 5.8, 3.4, "La ReLU borra negativos",
         "Los bordes de claro a oscuro dan valores negativos: la ReLU los convierte en 0.", ORANGE, size=19, head_size=23)
    card(s, LM + 6.0, 1.95, 5.83, 3.4, "Solo compara izquierda y derecha",
         "Los bordes horizontales no cambian de izquierda a derecha: este kernel no los ve.", BLUE, size=19, head_size=23)
    text(s, LM, 5.65, CW, 0.7, "Es la respuesta a la pregunta del notebook 3_1.", 19, GRAY, True)

    practica(d, "3_1_capa_convolucional", "notebooks · 30 min · 4 puntos",
             [("TODO 1 pt", "correlacionPixel: dos for de −k a k"), ("TODO 1 pt", "G de ceros del tamaño de I"),
              ("TODO 1 pt", "recortar las orillas: G[k:m-k, k:n-k]"), ("1 pt", "pregunta de la ReLU")],
             "# comprobaciones\nimagen: (256, 256) uint8\nsalida: (254, 254)\n\n# resultado debe ser de NumPy:\nresultado = np.array(sumatoria)",
             "Tras la ReLU se ven solo algunos bordes verticales, como en files/ccnout.png.", "Diapositivas 7 a 11.")
    descanso(d, "aprender el kernel")

    # 14 idea
    s = d.slide(notes="Nadie elige los números del kernel: se aprenden. Son los pesos de la capa convolucional.")
    title(s, "Los números del kernel se aprenden", "Aprender el kernel")
    grid(s, LM + 0.3, 2.1, 0.95, [["w₁", "w₂", "w₃"], ["w₄", "w₅", "w₆"], ["w₇", "w₈", "w₉"]], 18, fill=PALEORANGE)
    text(s, 4.6, 2.0, 7.98, 4.4, ["En una red convolucional nadie elige los números del kernel.",
                                  ("Son los pesos de la capa: se aprenden con descenso por gradiente.",
                                   {"bold": True, "color": ORANGE}),
                                  "Igual que en la clase 4, pero ahora la “predicción” es una imagen entera."],
         20, GRAY, space=16)

    # 15 gradiente
    s = d.slide(notes="El mismo peso se usa en todas las posiciones; por la regla de la cadena su gradiente suma la contribución "
                      "de cada posición.")
    title(s, "El gradiente de un peso del kernel")
    rect(s, LM, 1.95, CW, 1.3, NAVY, radius=0.06)
    text(s, LM, 1.95, CW, 1.3, "∂ECM/∂K[u,v] = (2/N) · Σ (P − T) · [G > 0] · I[i+u, j+v]", 22, CREAM, True, MONO,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    table(s, LM, 3.5, CW, [["Pieza", "Significado"], ["P − T", "error en cada píxel (predicción − objetivo)"],
                           ["[G > 0]", "1 si la ReLU dejó pasar, 0 si no (derivada de la ReLU)"],
                           ["I[i+u, j+v]", "el píxel que se multiplicó por ese peso"]], 18, [2.8, 9.03], 0.58)
    text(s, LM, 5.95, CW, 0.5, Runs([("Luego:  ", {}), ("K ← K − η · gradiente", {"font": MONO, "bold": True, "color": ORANGE})]),
         19, GRAY)

    # 16 trampas
    s = d.slide(notes="practica_07 muestra el efecto de centrar: sin centrar, diverge.")
    title(s, "Trampas y trucos")
    card(s, LM, 1.95, 5.8, 4.3, "Trampas", bullets([Runs([B("ReLU muerta: "), ("todo G negativo → sin gradiente.", {})]),
                                                    Runs([B("Escala: "), ("píxeles 0–255 → gradientes enormes.", {})]),
                                                    Runs([B("Lentitud: "), ("píxel por píxel tarda minutos.", {})])]),
         ORANGE, size=18, head_size=24)
    card(s, LM + 6.0, 1.95, 5.83, 4.3, "Trucos", bullets([Runs([B("Normalizar: "), ("dividir entre 255.", {})]),
                                                         Runs([B("Centrar: "), ("restar el promedio.", {})]),
                                                         Runs([B("Vectorizar "), ("y usar ", {}), B("momentum"), (".", {})])]),
         BLUE, size=18, head_size=24)

    # 17 vectorizar
    s = d.slide(notes="9 (o 25) versiones desplazadas de la imagen; la correlación es su suma ponderada; el gradiente de cada "
                      "peso, un promedio sobre una matriz.")
    title(s, "Vectorizar: versiones desplazadas")
    code(s, LM, 1.95, 7.3, 3.2, """# una versión desplazada por cada peso (u, v)
d = {(u, v): I[k+u:m-k+u, k+v:n-k+v]
     for u in range(-k, k+1) for v in range(-k, k+1)}

G = sum(K[u+k, v+k] * d[(u, v)] for (u, v) in d)""", 15)
    text(s, 8.35, 1.95, 4.23, 4.4, ["La correlación es la suma de cada versión por su peso.",
                                    "El gradiente de cada peso es un promedio sobre una matriz completa.",
                                    ("Milisegundos por época.", {"bold": True, "color": ORANGE})], 18, GRAY, space=12)

    # 18 resultados
    s = d.slide(notes="practica_07: recupera Sobel exacto en ruido centrado. Reto 3_2: foto real, 5×5, ReLU, momentum 0.9, η 2, "
                      "2000 épocas: ECM 31600 → 29.")
    title(s, "Resultado: el descenso descubre el filtro de Sobel")
    text(s, LM, 1.85, 5.6, 0.4, "Sobel (objetivo)", 17, INK, True)
    grid(s, LM, 2.3, 0.8, [[-1, -2, -1], [0, 0, 0], [1, 2, 1]], 17, fill=CARD)
    text(s, 3.6, 1.85, 2.6, 0.4, "Aprendido (reto 3_2)", 17, INK, True)
    grid(s, 3.6, 2.3, 0.8, [["−0.86", "−1.77", "−0.89"], ["−0.03", "−0.01", "0.04"], ["0.93", "1.79", "0.84"]], 14,
         fill=PALEORANGE)
    text(s, 6.6, 1.95, 5.98, 4.4, [Runs([B("practica_07: "), ("recupera Sobel exacto (ECM 0.97 → 0).", {})]),
                                   Runs([B("Reto 3_2: "), ("ECM 31 600 → 29; la imagen predicha es casi idéntica.", {})]),
                                   ("Una CNN profunda hace esto con muchos kernels y muchas capas: bordes → formas → objetos.",
                                    {"bold": True, "color": ORANGE})], 18, GRAY, space=12)

    practica(d, "3_2 · reto + practica_07", "notebooks · 20 min · reto (puntos extra)",
             [("1", "Normaliza y centra la entrada"), ("2", "Vectoriza con versiones desplazadas"),
              ("3", "Descenso con momentum β 0.9, η 2, 2000 épocas")],
             "# referencia del reto\nECM inicial ≈ 31600\nECM final   ≈ 29\nkernel ≈ Sobel en el centro\n\n# demo:\n# python docs/practica_07.py --graficar",
             "Guía con la estrategia completa: docs/guias_notebooks/NB_3_2.", "Diapositivas 14 a 18.")
    quiz(d, ["¿Por qué no usar capas densas para imágenes?", "¿Cuánto mide la salida de una imagen 7 × 7 con un kernel 3 × 3?",
             "¿Qué detecta el kernel con filas −1 0 1?", "¿Por qué se ven solo algunos bordes tras la ReLU?",
             "¿Qué son los “pesos” de una capa convolucional?"],
         "Respuestas: 1) demasiados pesos e ignoran la vecindad. 2) 5 × 5. 3) bordes verticales. 4) la ReLU borra los "
         "negativos. 5) los números del kernel.")
    cierre(d, ["Convolución: un filtro pequeño recorre la imagen con los mismos pesos.",
               "Los kernels detectan patrones y se aprenden con descenso por gradiente.",
               "Las redes profundas apilan muchas capas convolucionales."],
           "Fin del curso introductorio. Siguiente: aprendizaje profundo.",
           "notebook 3_1 (4 pts) + reto 3_2 (extra)", "Goodfellow et al., Deep Learning, cap. 9 (redes convolucionales)",
           "Cierre del curso: felicita al grupo; recorrido desde McCulloch y Pitts hasta CNN.")
    return d


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "entregables"
    os.makedirs(out, exist_ok=True)
    for name, fn in [("Clase1_Diapositivas", clase1), ("Clase2_Diapositivas", clase2),
                     ("Clase3_Diapositivas", clase3), ("Clase4_Diapositivas", clase4),
                     ("Clase5_Diapositivas", clase5), ("Clase6_Diapositivas", clase6),
                     ("Clase7_Diapositivas", clase7)]:
        path = os.path.join(out, name + ".pptx")
        print(path, fn().save(path), "diapositivas")
