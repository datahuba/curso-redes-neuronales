"""Genera las diapositivas de las clases en PowerPoint (16:9).

Uso:  python tools/build_decks.py            -> entregables/Clase1..7_Diapositivas.pptx (enfoque proyecto: reconocedor de dígitos)
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




# ================================================================ PROYECTO: figuras reales generadas con NumPy
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(RAIZ, "entregables", "_figuras")


def figuras():
    """Genera las imágenes de las diapositivas con los datos reales (MNIST). Tarda ~20 s."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    sys.path.insert(0, os.path.join(RAIZ, "proyecto"))
    from digitos import cargar_mnist

    os.makedirs(FIG, exist_ok=True)
    X, y, Xt, yt = cargar_mnist()
    Xf = X.reshape(-1, 784) / 255

    def guardar(nombre, fig):
        fig.savefig(os.path.join(FIG, nombre), dpi=160, bbox_inches="tight", transparent=True)
        plt.close(fig)

    def fila(imgs, titulos, nombre, cmap="gray", sim=False, cols=10):
        filas = (len(imgs) + cols - 1) // cols
        fig, ax = plt.subplots(filas, cols, figsize=(1.2 * cols, 1.4 * filas), squeeze=False)
        for a, im, t in zip(ax.flat, imgs, titulos):
            v = abs(im).max() if sim else None
            a.imshow(im.reshape(28, 28) if im.size == 784 else im, cmap=cmap,
                     vmin=-v if sim else None, vmax=v if sim else None)
            a.set_title(str(t), fontsize=12)
        for a in ax.flat:
            a.axis("off")
        guardar(nombre, fig)

    fila(X[:20], y[:20], "mnist.png")
    plantillas = np.array([Xf[y == d].mean(axis=0) for d in range(10)])
    fila(plantillas, range(10), "plantillas.png")

    # perceptrón 0 vs 1, una época
    f = (y == 0) | (y == 1)
    w, b = np.zeros(784), 0.0
    for xi, yi in zip(Xf[f], (y[f] == 1).astype(int)):
        e = yi - int(xi @ w + b > 0)
        w, b = w + 0.1 * e * xi, b + 0.1 * e
    fig, a = plt.subplots(figsize=(3.2, 3.2))
    a.imshow(w.reshape(28, 28), cmap="bwr", vmin=-abs(w).max(), vmax=abs(w).max()); a.axis("off")
    guardar("pesos_perceptron.png", fig)

    # descenso por gradiente con tres eta
    fig, ax = plt.subplots(1, 3, figsize=(11, 3))
    ws = np.linspace(-5, 11, 200)
    for a, eta in zip(ax, [0.1, 0.5, 1.05]):
        c = [-4.0]
        for _ in range(20):
            c.append(c[-1] - eta * 2 * (c[-1] - 3))
        c = np.array(c)
        a.plot(ws, (ws - 3) ** 2, color="gray"); a.plot(c, (c - 3) ** 2, "o-", color="#C4621D", ms=4)
        a.set_ylim(0, 70); a.set_xlim(-5, 11); a.set_title(f"eta = {eta}", fontsize=14); a.set_yticks([])
    guardar("descenso.png", fig)

    z = np.linspace(-8, 8, 200)
    fig, a = plt.subplots(figsize=(5, 3))
    a.plot(z, 1 / (1 + np.exp(-z)), lw=3, color="#2F6FB0", label="sigmoide")
    a.plot(z, (z > 0).astype(int), "--", color="#C4621D", label="escalón (perceptrón)")
    a.legend(fontsize=11); a.grid(alpha=0.3)
    guardar("sigmoide.png", fig)

    # 10 neuronas (softmax), una época de mini-lotes
    Y = np.eye(10)[y]
    W, bb = np.zeros((784, 10)), np.zeros(10)
    for i in range(0, 60000, 128):
        Z = Xf[i:i + 128] @ W + bb
        P = np.exp(Z - Z.max(1, keepdims=True)); P /= P.sum(1, keepdims=True)
        W -= 0.5 * Xf[i:i + 128].T @ (P - Y[i:i + 128]) / len(P); bb -= 0.5 * (P - Y[i:i + 128]).mean(0)
    fila(W.T, range(10), "pesos10.png", cmap="bwr", sim=True)

    mov = np.roll(Xt[:6], (3, 3), axis=(1, 2))
    fila(np.concatenate([Xt[:6], mov]), ["original"] * 6 + ["movida"] * 6, "movidas.png", cols=6)

    from numpy.lib.stride_tricks import sliding_window_view
    filtros = [("original", None), ("verticales", [[1, 0, -1], [2, 0, -2], [1, 0, -1]]),
               ("horizontales", [[1, 2, 1], [0, 0, 0], [-1, -2, -1]]), ("desenfoque", np.ones((3, 3)) / 9)]
    img = X[0] / 255
    out = [img if f is None else (sliding_window_view(img, (3, 3)) * np.array(f)).sum(axis=(2, 3)) for _, f in filtros]
    fila(out, [n for n, _ in filtros], "filtros.png", cols=4)


def foto(s, nombre, x, y, w=None, h=None):
    pic = s.shapes.add_picture(os.path.join(FIG, nombre), Inches(x), Inches(y), Inches(w) if w else None,
                               Inches(h) if h else None)
    if pic.left + pic.width > Inches(RM):          # nunca salirse del margen derecho
        k = (Inches(RM) - pic.left) / pic.width
        pic.width, pic.height = int(pic.width * k), int(pic.height * k)


# ================================================================ PROYECTO: plantillas de diapositiva
RECORRIDO = [("1", "Plantillas promedio", "82 %"), ("2", "Una neurona (perceptrón)", "0 vs 1: 99.8 %"),
             ("3", "Sigmoide + descenso por gradiente", "3 vs 5: 96 %"), ("4", "10 neuronas + softmax → ¡a dibujar!", "92 %"),
             ("5", "Capa oculta + retropropagación", "97 %"), ("6", "Optimizadores (momentum)", "97.6 %"),
             ("7", "Convolución + aumento de datos", "resiste dibujos movidos")]


def mapa(d, n, notes="El mapa del proyecto: cada clase agrega una pieza y la precisión sube."):
    s = d.slide(notes=notes)
    title(s, "Dónde estamos en el proyecto", "Reconocedor de dígitos")
    rows = [["Clase", "Pieza que agregamos", "Resultado"]] + [list(r) for r in RECORRIDO]
    table(s, LM, 1.8, CW, rows, 18, [1.3, 7.33, 3.2], 0.58, highlight=[n] if n else None,
          align=[PP_ALIGN.CENTER, None, PP_ALIGN.CENTER])


def problema(d, eyebrow, pregunta, detalle, notes):
    s = d.slide(True, notes=notes)
    text(s, LM, 1.2, CW, 0.5, eyebrow.upper(), 18, AMBER, True)
    text(s, LM, 1.9, CW, 2.4, pregunta, 44, CREAM, True, line=1.05)
    text(s, LM, 4.6, CW, 1.8, detalle, 22, SOFT, space=8)
    return s


def concepto(d, t, eyebrow, puntos, derecha=None, notes="", fig=None, formula=None, remate=None, ancho=6.2):
    """Izquierda: puntos clave. Derecha: código, fórmula o figura."""
    s = d.slide(notes=notes)
    title(s, t, eyebrow)
    text(s, LM, 1.95, ancho, 4.3, bullets(puntos), 19, GRAY, space=12)
    x = LM + ancho + 0.3
    w = RM - x
    if formula:
        rect(s, x, 1.95, w, 1.5, NAVY, radius=0.06)
        text(s, x, 1.95, w, 1.5, formula, 24, CREAM, True, MONO, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    if derecha:
        y = 3.65 if formula else 1.95
        code(s, x, y, w, 6.3 - y, derecha, 15)
    if fig:
        foto(s, fig, x, 3.65 if formula else 1.95, w=w)
    if remate:
        text(s, LM, 6.2, CW, 0.6, remate, 21, ORANGE, True)
    return s


def figura(d, t, eyebrow, fig, pie, notes, h=3.6):
    s = d.slide(notes=notes)
    title(s, t, eyebrow)
    foto(s, fig, LM, 1.85, h=h)
    text(s, LM, 1.95 + h, CW, 1.0, pie, 20, GRAY)
    return s


def resultado(d, numero, linea, sub, notes):
    s = d.slide(True, notes=notes)
    text(s, LM, 1.7, CW, 2.0, numero, 110, AMBER, True, align=PP_ALIGN.CENTER)
    text(s, LM, 3.9, CW, 0.8, linea, 30, CREAM, True, align=PP_ALIGN.CENTER)
    text(s, LM, 4.8, CW, 1.2, sub, 20, SOFT, align=PP_ALIGN.CENTER)


def arranque(d, nb, mision, falla, notes):
    """Segunda diapositiva de cada clase: directo al teclado."""
    s = d.slide(True, notes=notes)
    text(s, LM, 0.9, CW, 0.5, "MANOS AL TECLADO", 18, AMBER, True)
    text(s, LM, 1.5, CW, 1.4, ["Abre  " + nb, "y ejecuta la primera celda"], 40, CREAM, True, line=1.05)
    rect(s, LM, 3.75, CW, 2.5, RGBColor(0x22, 0x34, 0x5C), radius=0.06)
    text(s, LM + 0.35, 3.95, CW - 0.7, 2.1,
         [Runs([C("Hoy construimos: ", AMBER), (mision, {})]), Runs([C("Lo que todavía falla: ", AMBER), (falla, {})]),
          ("La teoría llega en pausas cortas, justo cuando el ejercicio la necesita.", {"color": MUTED, "size": 17})],
         21, CREAM, space=12)


def paso(d, k, titulo, meta, todos, check, pistas="", notes="", size=18):
    """Diapositiva de práctica: qué hacer en el notebook (izquierda) y qué deben ver (derecha)."""
    s = d.slide(True, notes=notes)
    title(s, f"Paso {k} · {titulo}", meta, size=32 if len(titulo) < 34 else 27)
    text(s, LM, 1.95, 6.0, 2.6, [Runs([C(t + "   ", AMBER), (b, {})]) for t, b in todos], size, SOFT, space=12)
    if pistas:
        text(s, LM, 4.7, 6.0, 1.5, pistas, 16, MUTED)
    text(s, 7.0, 1.6, 5.58, 0.35, "LO QUE DEBES VER", 13, MUTED, True)
    code(s, 7.0, 1.95, 5.58, 3.3, check, 15)
    return s


def capsula(d, minutos, t, puntos, **kw):
    """Teoría en pocos minutos, justo antes (o justo después) del ejercicio que la usa."""
    return concepto(d, t, f"Pausa · teoría en {minutos} min", puntos, **kw)


def final(d, n, take, proxima, tarea, apoyo, notes):
    mapa(d, n, notes="Así avanzó el proyecto hoy. Señala la fila de la clase.")
    cierre(d, take, proxima, tarea, apoyo, notes)


# ================================================================ CLASE 1
def clase1():
    d = Deck("Introducción a las Redes Neuronales  ·  Clase 1")
    cover(d, "CLASE 1  ·  EL PROYECTO", "Vamos a construir", "una IA que lee números",
          "Hoy: instalar, conocer los datos y una primera IA… sin neuronas",
          "Antes de hablar: abre dibujar.py (guía, Parte A.5) y pide a un alumno que dibuje un número.")
    problema(d, "La demo · 2 min", "Dibuja un número.\nLa red lo adivina.",
             ["Esto lo van a programar ustedes, línea por línea, en Python.", "Empezamos ya: primero, a instalar."],
             "Demo en vivo con dibujar.py. Nada de teoría todavía: directo a instalar.")
    s = d.slide(notes="Sigue la Parte A de la guía. Quien se trabe más de 10 min, sigue en Colab.")
    title(s, "Paso 1 · Instalar (elige un camino)", "40 min")
    card(s, LM, 1.95, 5.8, 3.9, "Colab (sin instalar)",
         bullets(["colab.research.google.com", "Archivo → Abrir cuaderno → GitHub", "datahuba/curso-redes-neuronales",
                  "proyecto/P1_conocer_los_datos.ipynb"]), BLUE, size=17)
    card(s, LM + 6.03, 1.95, 5.8, 3.9, "Tu computadora (recomendado)",
         bullets(["Anaconda + Git + VS Code", "conda create --name nni python=3.11",
                  "git clone …/curso-redes-neuronales", "pip install -r requirements.txt"]), ORANGE, size=17)
    paso(d, 2, "abrir el proyecto", "P1 · 5 min",
         [("Abre", "proyecto/P1_conocer_los_datos.ipynb"), ("Kernel", "nni (arriba a la derecha)"),
          ("Ejecuta", "las dos primeras celdas con Shift + Enter")],
         "X_train: (60000, 28, 28)  y_train: (60000,)\nX_test:  (10000, 28, 28)  y_test:  (10000,)",
         "La primera vez descarga 11 MB de datos.", notes="Quien vea esto, ya terminó de instalar.")
    paso(d, 3, "mirar los datos", "P1 · secciones 1 y 2 · 15 min",
         [("Ejecuta", "mostrar(...) y la tabla de números"), ("Ej. 1", "¿cuántos ejemplos hay de cada dígito?")],
         "[5923 6742 5958 6131 5842 5421 5918 6265 5851 5949]\nOK: hay unos 6 000 ejemplos de cada dígito",
         "Busca el 5 dentro de la tabla de números.", notes="Primero que miren. La explicación viene en la pausa siguiente.")
    s = d.slide(notes="Explica lo que acaban de ver. 0 = negro, 255 = blanco. Y por qué hay datos de entrenamiento y de prueba.")
    title(s, "Una imagen es una tabla de números", "Pausa · teoría en 3 min")
    sys.path.insert(0, os.path.join(RAIZ, "proyecto"))
    from digitos import cargar_mnist
    grid(s, LM, 1.85, 0.34, cargar_mnist()[0][0][6:20, 9:23].tolist(), 8, shade=True)
    text(s, 6.0, 1.95, 6.58, 4.2, bullets(["28 × 28 = 784 números entre 0 (negro) y 255 (blanco).",
                                          Runs([B("Para la red: "), ("una fila de 784 números entre 0 y 1.", {})]),
                                          Runs([B("60 000 para aprender, 10 000 para el examen: "),
                                                ("si el examen trae las preguntas de la práctica, no sabes si entendió.", {})])]),
         19, GRAY, space=14)
    paso(d, 4, "preparar los datos", "P1 · Ejercicio 2 · 10 min",
         [("Ej. 2", "aplanar a 784 y dividir entre 255")],
         "X = X_train.reshape(60000, 784) / 255\n\nOK: las imágenes son filas de 784\nOK: los valores van de 0 a 1",
         "Error típico: reshape(784) sin decir cuántas imágenes son.")
    descanso(d, "nuestra primera IA")
    capsula(d, 3, "¿Cómo le explicas a una computadora qué es un 7?",
            ["Con reglas: «una raya arriba y una diagonal»… ¿y el 7 con rayita?",
             Runs([B("Aprender de ejemplos: "), ("la máquina saca la regla de los datos.", {})]),
             Runs([B("Idea de hoy: "), ("promediar los 6 000 «tres» → el tres típico (plantilla).", {})])],
            fig="plantillas.png", formula="ejemplos + respuestas\n→ la máquina saca la regla",
            notes="Pregunta primero: si promedio los 6 000 tres, ¿qué saldrá? Luego muestra las plantillas.")
    paso(d, 5, "la IA de plantillas", "P1 · Ejercicios 3 y 4 · 30 min",
         [("Ej. 3", "plantilla de cada dígito: X[y_train == d].mean(axis=0)"),
          ("Ej. 4", "predecir(x): la plantilla más parecida (argmin)"), ("Examen", "medir la precisión")],
         "La IA dice: 7  · La respuesta correcta es: 7\nPrecisión: 82.0%\nOK: la IA de plantillas acierta más del 80 %",
         "Mira los errores: ¿tú también los confundirías?", notes="Mirar los errores juntos es lo más valioso de la clase.")
    resultado(d, "82 %", "sin una sola neurona", "Pero las plantillas nunca cambian: si se equivocan, no aprenden nada.",
              "¿Es bueno? Al azar sería 10 %. Pero 1 de cada 5 mal es mucho para leer cheques.")
    final(d, 1, ["Una imagen es una tabla de números → una fila de 784.", "Aprender de datos, no de reglas.",
                 "Medir con datos que no vio: la precisión."],
          "Próxima clase: una neurona que corrige sus pesos cuando se equivoca.",
          "terminar P1. Desafío: ¿y si usas el producto punto (plantillas @ x) con argmax?",
          "introducción del libro del Dr. Irving Vasquez (opcional).", "Vocabulario: dato, etiqueta, entrenamiento, prueba, precisión.")
    return d


# ================================================================ CLASE 2
def clase2():
    d = Deck("Introducción a las Redes Neuronales  ·  Clase 2")
    cover(d, "CLASE 2  ·  UNA NEURONA", "Una neurona que", "aprende de sus errores",
          "El perceptrón: de pesos a mano a pesos aprendidos", "Directo al notebook.")
    arranque(d, "proyecto/P2_una_neurona", "una neurona que distingue el 0 del 1 y aprende de sus errores.",
             "las plantillas de la Clase 1 se equivocan y no aprenden nada.",
             "Que abran el notebook mientras dices la misión (1 min).")
    paso(d, 1, "compuerta AND a mano", "P2 · sección 1 · 10 min",
         [("Calentamiento", "busca w y b para que solo [1, 1] dé 1"), ("Pista", "prueba pesos 1 y piensa el sesgo")],
         "x1 x2 → salida\n[0 0] → 0\n[0 1] → 0\n[1 0] → 0\n[1 1] → 1\nOK: tu neurona es una compuerta AND",
         "Sin explicación previa: que prueben números.", notes="5 minutos de prueba y error. Una solución: 1, 1 y −1.5.")
    capsula(d, 3, "Lo que acabas de construir: una neurona", [
        Runs([B("Pesos w: "), ("cuánto importa cada entrada (pueden ser negativos).", {})]),
        Runs([B("Sesgo b: "), ("qué tan fácil es decir que sí.", {})]),
        Runs([B("Decide: "), ("1 si la suma pasa de 0.", {})]),
        "¿Y la compuerta OR? Infinitas respuestas → se puede aprender."],
        derecha="salida = (x @ w + b > 0).astype(int)\n\n# @ = multiplicar casilla por casilla\n#     y sumar todo",
        formula="x₁w₁ + x₂w₂ + … + b > 0 ?",
        notes="Explica sobre lo que ya hicieron. McCulloch y Pitts (1943): pesos fijos; Rosenblatt (1958): aprenderlos.")
    paso(d, 2, "la neurona con imágenes", "P2 · sección 2 y Ejercicio 1 · 15 min",
         [("Datos", "solo ceros y unos: y = 1 si es un 1"), ("Ej. 1", "neurona(x, w, b) para muchas imágenes a la vez")],
         "Precisión con pesos al azar: ~50%\nOK: la neurona devuelve 0/1 para cada fila",
         "Con 784 entradas nadie busca los pesos a mano.", notes="Error típico: usar if, que falla con muchas imágenes.")
    descanso(d, "que la neurona aprenda sola")
    capsula(d, 5, "La regla de Rosenblatt", [
        "Acertó → no se toca nada.", "Dijo 0 y era 1 (error +1) → sube los pesos de los píxeles encendidos.",
        "Dijo 1 y era 0 (error −1) → bájalos.", Runs([B("η (eta): "), ("tamaño de cada corrección.", {})])],
        derecha="x = [1, 0, 1]   w = [0, 0, 0]   b = 0\ny = 1  → dijo 0 → error = +1\nw = [0.1, 0, 0.1]   b = 0.1\n"
                "→ suma = 0.3 > 0 → dice 1",
        formula="error = y − ŷ\nw ← w + η·error·x", notes="El ejemplo de 3 píxeles en el pizarrón, y directo al Paso 3.")
    paso(d, 3, "entrenar", "P2 · Ejercicio 2 · 20 min",
         [("Ej. 2", "completa la corrección de w y de b"), ("Mira", "cómo bajan los errores por época")],
         "época 1: se equivocó 45 veces\népoca 2: se equivocó 24 veces\n...\nPrecisión en el examen: 99.81%",
         notes="Errores típicos: w = eta*error*xi (falta sumar el w anterior); usar y en lugar de yi.")
    s = d.slide(notes="Rojo en el centro (donde el 1 tiene tinta), azul en el anillo (donde el 0 tiene tinta).")
    title(s, "¿Qué aprendió? Los pesos como imagen", "P2 · sección 4")
    foto(s, "pesos_perceptron.png", LM, 1.8, h=4.3)
    text(s, 5.6, 2.0, 6.98, 4.0, bullets([Runs([C("Rojo", ORANGE), (": «si hay tinta acá, digo 1»", {})]),
                                          Runs([C("Azul", BLUE), (": «si hay tinta acá, digo 0»", {})]),
                                          "Nadie le dijo dónde mirar: lo sacó de los ejemplos."]), 21, GRAY, space=14)
    paso(d, 4, "desafío 3 vs 5", "P2 · sección 5 · 20 min",
         [("Cambia", "A, B = 3, 5 y ejecuta todo"), ("Observa", "¿los errores por época llegan a cero?")],
         "época 1: se equivocó 823 veces\népoca 2: se equivocó 651 veces\népoca 3: se equivocó 636 veces\n# nunca se calma",
         "La regla solo sabe si acertó, no cuánto se equivocó.",
         notes="Precisión ~95 % pero no se estabiliza: mismo empujón por un error mínimo que por uno enorme.")
    final(d, 2, ["Neurona = suma ponderada + decisión.", "Aprender = corregir los pesos cuando se equivoca.",
                 "Límite: solo dice 0/1 y no mide cuánto se equivocó."],
          "Próxima clase: «es un 5 con 80 % de seguridad» y bajar el error poco a poco.",
          "terminar P2; probar 3 vs 5 con epocas=10.", "refuerzo: notebooks 1_01, 1_02, 1_03_1 y 1_03_2 (opcional).",
          "Pregunta de salida: ¿cómo sabría cuánto se equivocó?")
    return d


# ================================================================ CLASE 3
def clase3():
    d = Deck("Introducción a las Redes Neuronales  ·  Clase 3")
    cover(d, "CLASE 3  ·  DESCENSO POR GRADIENTE", "Aprender bajando", "la montaña",
          "Sigmoide, error medible y descenso por gradiente", "Directo al notebook.")
    arranque(d, "proyecto/P3_aprender_con_gradiente", "una neurona que dice «es un 5 con 80 % de seguridad» y aprende "
             "bajando su error.", "el perceptrón con 3 vs 5 nunca se calma: no sabe cuánto se equivocó.",
             "Recuerda en una frase los errores por época del perceptrón con 3 vs 5.")
    paso(d, 1, "la sigmoide", "P3 · sección 1 · 10 min",
         [("Ej. 1", "escribe sigmoide(z) con np.exp"), ("Mira", "la gráfica: compárala con el escalón")],
         "OK: la sigmoide va de 0 a 1", "La fórmula está en el notebook.", notes="Que la escriban; la explicación viene ahora.")
    capsula(d, 3, "De «sí/no» a «qué tan seguro»", [
        "Un escalón suavizado: muy negativo → 0, muy positivo → 1, cero → 0.5.",
        "Se lee como probabilidad: 0.8 = «80 % seguro de que es un 5».",
        "Suave → si muevo un poco un peso, la salida cambia un poco: se puede medir hacia dónde mejorar."],
        formula="σ(z) = 1 / (1 + e⁻ᶻ)", fig="sigmoide.png")
    capsula(d, 3, "La montaña con niebla", [
        "Queremos llegar al fondo del valle: el error mínimo.", "Solo sentimos la pendiente bajo los pies.",
        "Paso cuesta abajo, volver a sentir, repetir.",
        Runs([B("Pendiente = derivada: "), ("hacia dónde sube y qué tan empinado.", {})])],
        derecha="E(w) = (w − 3)²       # error inventado\npendiente = 2·(w − 3)",
        formula="w ← w − η · pendiente", notes="Dibuja la parábola. En el fondo la pendiente es 0. Luego directo al Paso 2.")
    paso(d, 2, "bajar la montaña con un número", "P3 · sección 2 · 15 min",
         [("Ej. 2", "completa el paso: w = w − eta · pendiente"), ("Prueba", "eta = 0.01, 0.1, 0.5, 0.9, 1.05")],
         "eta = 0.1  → termina en w = 3.08\neta = 0.5  → termina en w = 3.00\neta = 1.05 → se aleja (diverge)\n"
         "OK: con eta = 0.1 llega cerca de w = 3",
         "¿Qué pasa con eta muy chico? ¿Y muy grande?")
    figura(d, "La tasa de aprendizaje lo es todo", "Puesta en común · 5 min", "descenso.png",
           [Runs([B("0.1: "), ("baja suave.   ", {}), B("0.5: "), ("llega de un salto.   ", {}), B("1.05: "),
                  ("rebota y se aleja.", {})]),
            ("Elegir eta es la decisión más importante al entrenar.", {"bold": True, "color": ORANGE})],
           "Que cuenten qué vieron con cada eta.", h=3.0)
    descanso(d, "la neurona que aprende con gradiente")
    capsula(d, 4, "La pendiente de la neurona", [
        Runs([B("Error (entropía cruzada): "), ("castiga estar muy seguro y equivocado.", {})]),
        Runs([B("Léanla: "), ("(lo que dijo − lo correcto) × entrada.", {})]),
        "¡Casi Rosenblatt! Pero p − y dice cuánto se equivocó."],
        derecha="p = sigmoide(X @ w + b)\ngrad_w = X.T @ (p - y) / len(X)\ngrad_b = np.mean(p - y)",
        formula="grad_w = Xᵀ(p − y) / n", notes="Para curiosos: la derivada de la sigmoide se cancela con la del logaritmo.")
    paso(d, 3, "entrenar 3 vs 5", "P3 · Ejercicio 3 · 25 min",
         [("Ej. 3", "predecir, calcular pendientes, dar el paso"), ("Mira", "la curva de aprendizaje")],
         "# la curva baja suave, sin saltos\nPrecisión 3 vs 5: 96.1%\nOK: el error baja y la neurona acierta más del 90 %",
         "¿Por qué baja rápido al principio y lento al final? Prueba eta = 5.",
         notes="Errores típicos: X @ (p - y) sin .T; no dividir por len(X).")
    paso(d, 4, "¿cuándo duda?", "P3 · sección 4 · 10 min",
         [("Ejecuta", "las 10 imágenes donde la neurona está menos segura"), ("Piensa", "¿tú también dudarías?")],
         "dudas = np.argsort(np.abs(p_test - 0.5))[:10]\nmostrar(Xt[dudas], ...)",
         "La red sabe cuándo no sabe: una ventaja enorme.")
    final(d, 3, ["Sigmoide → probabilidades.", "Error medible + descenso por gradiente → aprender poco a poco.",
                 "La curva de aprendizaje se mira siempre."],
          "Próxima clase: 10 neuronas, una por dígito… y van a dibujar sus números.",
          "terminar P3; probar 4 vs 9 y 1 vs 7: ¿cuál es el más difícil?", "refuerzo: notebooks 1_04 y 1_05 (opcional).",
          "Pregunta de salida: ¿qué pasa si eta es demasiado grande?")
    return d


# ================================================================ CLASE 4
def clase4():
    d = Deck("Introducción a las Redes Neuronales  ·  Clase 4")
    cover(d, "CLASE 4  ·  DIEZ NEURONAS", "Del 0 al 9", "¡y a dibujar!",
          "One-hot, softmax, mini-lotes y tu primera red que lee tus números", "Directo al notebook.")
    arranque(d, "proyecto/P4_diez_neuronas", "10 neuronas, una por dígito… y al final dibujas tus números.",
             "hasta ahora solo respondíamos sí o no (0 o 1, 3 o 5).", "Pregunta rápida: ¿cuántas neuronas para 10 dígitos?")
    paso(d, 1, "one-hot y softmax", "P4 · Ejercicios 1 y 2 · 20 min",
         [("Ej. 1", "one_hot(y) con np.eye(10)"), ("Ej. 2", "softmax: 10 puntajes → 10 probabilidades")],
         "[[0. 0. 0. 0. 0. 1. 0. 0. 0. 0.] ...\n[[0.66 0.24 0.1 ]]\nOK: one_hot(3) tiene un 1 en la casilla 3\n"
         "OK: cada fila suma 1",
         "Error típico: sum sin axis=1, keepdims=True.")
    capsula(d, 3, "Lo que acabas de programar", [
        Runs([B("One-hot: "), ("la respuesta en 10 casillas: 3 → [0,0,0,1,0,…].", {})]),
        Runs([B("Softmax: "), ("la exponencial hace todo positivo y exagera al ganador.", {})]),
        "Restar el máximo antes no cambia nada y evita números gigantes."],
        derecha="E = np.exp(Z - Z.max(axis=1, keepdims=True))\nP = E / E.sum(axis=1, keepdims=True)\n\n# [2, 1, 0.1] → [0.66, 0.24, 0.10]",
        formula="pₖ = eᶻᵏ / Σ eᶻ", notes="Haz [2, 1, 0.1] en el pizarrón.")
    capsula(d, 2, "La tabla de pesos y la misma pendiente", [
        Runs([B("W: "), ("784 × 10, una columna por neurona.", {})]), "X @ W + b → 10 puntajes por imagen.",
        "La pendiente es la de la Clase 3: error × entrada.",
        Runs([B("Mini-lotes: "), ("para corregir el rumbo no hace falta preguntar a 60 000; con 128 alcanza.", {})])],
        derecha="P = softmax(Xb @ W + b)\ngrad_W = Xb.T @ (P - Yb) / len(Xb)\ngrad_b = (P - Yb).mean(axis=0)",
        formula="grad_W = Xᵀ(P − Y) / n", notes="Destaca que la fórmula es idéntica a la de la Clase 3.")
    paso(d, 2, "entrenar por mini-lotes", "P4 · Ejercicio 3 · 20 min",
         [("Ej. 3", "el paso dentro del ciclo de lotes"), ("Mira", "el error por época y la precisión")],
         "época 1: error 0.35\n...\népoca 5: error 0.27\nPrecisión en los 10 dígitos: 92.2%",
         "De 82 % (plantillas) a 92 %.")
    descanso(d, "qué mira cada neurona… y a dibujar")
    figura(d, "Paso 3 · ¿Qué mira cada neurona?", "P4 · secciones 5 y 6 · 15 min", "pesos10.png",
           ["Fantasmas de cada dígito: compáralos con las plantillas de la Clase 1. Ahora hay azul: lo que resta.",
            ("Después: la matriz de confusión. ¿Con qué se confunde más?", {"bold": True, "color": ORANGE})],
           "Que encuentren las confusiones más grandes (4↔9, 3↔5, 7↔9).", h=1.6)
    s = d.slide(True, notes="Terminal en la carpeta proyecto/. En Colab: Paint + mi_numero.png + última celda.")
    title(s, "Paso 4 · ¡A dibujar!", "P4 · sección 7 · 30 min")
    code(s, LM, 1.9, 6.2, 2.4, "# en el notebook:\nguardar_pesos(W1=W, b1=b)\n\n# en una terminal, carpeta proyecto/:\npython dibujar.py", 18)
    text(s, 7.3, 1.9, 5.28, 3.6, ["Clic izquierdo: dibujar.", "Clic derecho: borrar.",
                                  ("Mini-competencia: ¿quién engaña a la red con un número que una persona leería?",
                                   {"color": AMBER, "bold": True}),
                                  ("Colab: dibuja en Paint, sube mi_numero.png y usa la última celda.", {"color": MUTED})],
         19, SOFT, space=12)
    resultado(d, "92 %", "y ya lee tus dibujos", "Pero cada neurona separa con una línea recta: entrenar más no ayuda.",
              "Pide que anoten qué dibujos la engañan: los usaremos en la Clase 5.")
    final(d, 4, ["10 neuronas + softmax = clasificador de 10 clases.", "Mini-lotes = entrenar rápido.",
                 "Límite: modelo lineal, se queda en ~92 %."],
          "Próxima clase: una capa oculta → de 92 % a 97 %.",
          "terminar P4 y traer 3 dibujos que engañan a la red.", "refuerzo: notebooks 1_06, 1_07 y 1_08 (opcional).",
          "¿Con qué dibujos falla más?")
    return d


# ================================================================ CLASE 5
def clase5():
    d = Deck("Introducción a las Redes Neuronales  ·  Clase 5")
    cover(d, "CLASE 5  ·  RED MULTICAPA", "La red de verdad", "capa oculta y retropropagación",
          "De 92 % a 97 %", "Directo al notebook.")
    arranque(d, "proyecto/P5_red_multicapa", "una red con capa oculta que pasa de 92 % a 97 %.",
             "el modelo de la Clase 4 se estanca en 92 %: cada neurona solo traza una línea recta.",
             "Que muestren un dibujo que engañó a la red de la Clase 4 (1 min) y a abrir el notebook.")
    paso(d, 1, "ReLU y la red de dos capas", "P5 · secciones 1 a 3 · 20 min",
         [("Ej. 1", "relu(Z) = max(0, Z)"), ("Mira", "los tamaños de W1, b1, W2, b2"), ("Ej. 2", "adelante(red, X): las 3 líneas")],
         "W1 (784, 128)\nb1 (128,)\nW2 (128, 10)\nb2 (10,)\n[[0.14 0.14 0.09 ...]]   # sin entrenar: ~0.1\n"
         "OK: adelante() da 10 probabilidades por imagen",
         "Regla de tamaños: los números de adentro deben coincidir.")
    s = d.slide(notes="Explica lo que acaban de armar. Analogía de la fábrica: 128 inspectores detectan rasgos; el jefe decide con "
                      "sus informes. Sin ReLU, dos capas = una sola.")
    title(s, "Lo que armaste: inspectores de rasgos", "Pausa · teoría en 4 min")
    red(s, 1.4, 2.0, 5.0, 3.4, [5, 4, 3], ["imagen (784)", "oculta (128)", "salida (10)"])
    text(s, 7.6, 2.0, 4.98, 4.3, bullets(["Cada neurona oculta aprende un rasgo: un círculo arriba, una raya…",
                                          "La salida decide con esos rasgos, no con píxeles sueltos.",
                                          Runs([B("Sin ReLU: "), ("dos capas = una sola (otra vez lineal).", {})]),
                                          Runs([B("Nadie les dice qué buscar: "), ("lo aprenden.", {})])]), 19, GRAY, space=14)
    descanso(d, "retropropagación")
    s = d.slide(notes="El corazón del curso. Primero la idea sin fórmulas: la culpa de cada inspector depende de cuánto pesaba su informe "
                      "y de si estaba encendido. Luego los 5 pasos, marcando la red hacia atrás. Y directo al Paso 2.")
    title(s, "Retropropagación: repartir la culpa hacia atrás", "Pausa · teoría en 8 min")
    table(s, LM, 1.85, CW, [["Paso", "Código", "En palabras"],
                            ["1", "dZ2 = (P - Y) / n", "error de la salida (como en la Clase 4)"],
                            ["2", "dW2 = A1.T @ dZ2", "pendiente capa 2: error × entrada"],
                            ["3", "dA1 = dZ2 @ W2.T", "culpa de cada neurona oculta"],
                            ["4", "dZ1 = dA1 * (Z1 > 0)", "si estaba apagada, culpa 0"],
                            ["5", "dW1 = X.T @ dZ1", "pendiente capa 1: ¡la misma receta!"]],
          18, [1.0, 4.6, 6.23], 0.58, highlight=[3])
    text(s, LM, 5.55, CW, 0.8, "No hay matemática nueva: la regla de la cadena, capa por capa.", 21, ORANGE, True)
    paso(d, 2, "retropropagación", "P5 · Ejercicio 3 · 25 min",
         [("Ej. 3", "los 5 pasos, una línea cada uno"), ("Verifica", "mover un peso 0.00001 y medir")],
         "W1  tu función: -0.001241\n    a mano:     -0.001241\nOK: la pendiente de W1 es correcta\n"
         "W2  tu función:  0.000960\n    a mano:      0.000960\nOK: la pendiente de W2 es correcta",
         "Así depuran redes los profesionales.",
         notes="Errores típicos: A1 @ dZ2 sin .T; dZ2 @ W2 sin .T; dZ1 = dA1 * Z1 (debe ser la máscara Z1 > 0).")
    paso(d, 3, "entrenar y dibujar", "P5 · secciones 5 y 6 · 25 min",
         [("Entrenar", "el mismo ciclo de la Clase 4"), ("Dibujar", "guardar_pesos(**red) → python dibujar.py")],
         "época 1: precisión en el examen 93.99%\népoca 3: precisión en el examen 96.38%\n"
         "época 5: precisión en el examen 97.20%\nOK: la red multicapa supera el 96 %",
         "Prueba los dibujos que engañaban a la red de la Clase 4.")
    resultado(d, "97 %", "con una capa oculta", "92 % → 97 %: de 8 errores cada 100 a 3.",
              "Si sobra tiempo: experimentos de la sección 7 en grupos.")
    final(d, 5, ["Capa oculta = rasgos aprendidos.", "Retropropagación = repartir el error hacia atrás, misma receta.",
                 "Verificar pendientes numéricamente."],
          "Próxima clase: entrenar más rápido (optimizadores).",
          "terminar P5 + un experimento (ocultas, eta o sigmoide).", "refuerzo: notebooks 1_09, 1_10 y 1_11 con XOR (opcional).",
          "Pregunta: ¿por qué hace falta la ReLU?")
    return d


# ================================================================ CLASE 6
def clase6():
    d = Deck("Introducción a las Redes Neuronales  ·  Clase 6")
    cover(d, "CLASE 6  ·  OPTIMIZADORES", "Entrenar más rápido", "y mejor",
          "Momentum y decaimiento de la tasa, en una carrera", "Directo al notebook.")
    arranque(d, "proyecto/P6_entrenar_mejor", "una carrera entre formas de bajar la montaña, y la red definitiva (97.6 %).",
             "con eta chico tarda una eternidad; con eta grande, rebota.",
             "Recuerda que necesitan su P5 funcionando: pegan sus funciones en el Paso 1.")
    paso(d, 1, "traer tu red y correr SGD", "P6 · Paso 0 y secciones 1–2 · 15 min",
         [("Pega", "relu, softmax, crear_red, adelante y gradientes de tu P5"),
          ("Ejecuta", "la pista de carreras y el corredor SGD")],
         "OK: tus funciones de la Clase 5 están listas",
         "La red no cambia hoy: solo cómo bajamos la montaña.")
    capsula(d, 4, "Momentum: la pelota que rueda", [
        "Si la pendiente apunta siempre al mismo lado → acelera.", "Si cambia de lado (zigzag) → se cancela, se suaviza.",
        Runs([B("β = 0.9: "), ("recuerdo el 90 % de mi velocidad anterior.", {})])],
        derecha="v = memoria.get(k, 0)\nv = beta * v - eta * g[k]\nmemoria[k] = v\nred[k] += v",
        formula="v ← βv − η·pendiente\npeso ← peso + v",
        notes="Dibuja un valle alargado y el zigzag. Velocidad con pendiente 1 y eta 0.01: 0.01, 0.019, 0.027… → 0.1.")
    capsula(d, 2, "Decaimiento de la tasa", [
        "Como estacionar: lejos, rápido; cerca, despacio.", "eta0 = 0.3, k = 1 → 0.3, 0.15, 0.1, 0.075…"],
        derecha="eta = eta0 / (1 + k * epoca)", formula="η = η₀ / (1 + k·época)")
    paso(d, 2, "programar los dos corredores", "P6 · Ejercicios 1 y 2 · 20 min",
         [("Ej. 1", "momentum: velocidad acumulada"), ("Ej. 2", "decaimiento: eta que se achica")],
         "OK: fórmula revisada", "Error típico en momentum: sumar −v o guardar v antes de calcularla.")
    descanso(d, "¡la carrera!")
    s = d.slide(notes="Resultados reales con 20 000 imágenes y 5 épocas. Pregunta: ¿por qué momentum le gana a SGD con el mismo eta?")
    title(s, "Paso 3 · ¡La carrera!", "P6 · sección 5 · 15 min")
    table(s, LM, 1.95, CW, [["Corredor", "Error final", "Precisión"], ["SGD (eta 0.01)", "0.38", "90 %"],
                            ["Momentum (eta 0.01)", "0.15", "95 %"], ["Decaimiento (eta0 0.3)", "0.11", "96 %"]],
          22, [6.83, 2.5, 2.5], 0.75, highlight=[2], align=[None, PP_ALIGN.CENTER, PP_ALIGN.CENTER])
    text(s, LM, 5.2, CW, 1.0, "Momentum da velocidad sin volverse inestable.", 22, ORANGE, True)
    paso(d, 4, "experimentos y red definitiva", "P6 · secciones 6 y 7 · 35 min",
         [("Prueba", "SGD con eta 0.5 y 2.0; momentum con beta 0.99"),
          ("Definitiva", "momentum, 60 000 imágenes, 5 épocas → python dibujar.py")],
         "Precisión de la red definitiva: 97.64%\nOK: la red definitiva supera el 97 %",
         "Cada grupo cuenta su experimento en 1 minuto.")
    final(d, 6, ["Optimizador = cómo bajar la montaña; red y pendientes no cambian.",
                 "Momentum = velocidad acumulada · decaimiento = pasos que se achican.",
                 "Adam (el más usado) combina las dos ideas."],
          "Próxima clase: mueve tu dibujo 3 píxeles… y la red se rompe.",
          "terminar P6. Desafío: momentum + decaimiento juntos.", "refuerzo: notebooks 21, 22 y 23 (curvas en 2D, opcional).",
          "En PyTorch: torch.optim.Adam(...) es una línea.")
    return d


# ================================================================ CLASE 7
def clase7():
    d = Deck("Introducción a las Redes Neuronales  ·  Clase 7")
    cover(d, "CLASE 7  ·  CONVOLUCIÓN", "Ver formas,", "no posiciones",
          "Filtros convolucionales, pooling, aumento de datos… y el cierre del proyecto", "Directo al notebook.")
    arranque(d, "proyecto/P7_convolucion", "una red convolucional que reconoce el número aunque lo muevas.",
             "si mueves el dibujo 3 píxeles, tu red se derrumba. Lo vas a comprobar en 5 minutos.",
             "Necesitan su pesos.npz de la Clase 5 o 6. Antes de ejecutar la sección 1, que apuesten cuánto bajará.")
    figura(d, "Paso 1 · Mueve el dibujo 3 píxeles…", "P7 · sección 1 · 10 min", "movidas.png",
           [Runs([("Tu red densa: ", {}), C("97.6 %", BLUE), (" con las originales → ", {}), C("17 %", ORANGE),
                  (" con las movidas.", {})]),
            ("Aprendió dónde hay tinta, no qué forma tiene el número.", {"bold": True, "color": ORANGE})],
           "Cada píxel tiene su propio peso: la red no sabe que los vecinos están relacionados.", h=2.9)
    paso(d, 2, "la convolución a mano", "P7 · Ejercicio 1 · 15 min",
         [("Ej. 1", "recorte 3×3 por el filtro, todo sumado"), ("Mira", "bordes verticales, horizontales y desenfoque")],
         "salida[i, j] = (img[i:i+3, j:j+3] * filtro).sum()\n\nOK: la convolución suma 9 productos",
         "La fórmula está en el notebook.")
    capsula(d, 4, "Lo que hiciste: una lupa que recorre la imagen", [
        "El filtro 3 × 3 busca una sola cosa (un borde, una curva).",
        Runs([B("El mismo filtro en todas partes: "), ("lo detecta arriba o abajo.", {})]),
        "9 pesos en vez de 784.", Runs([B("La gran idea: "), ("la red aprende los 9 números del filtro.", {})])],
        fig="filtros.png", formula="salida[i, j] = Σ recorte · filtro", ancho=5.6,
        notes="Ejemplo en el pizarrón con el filtro de bordes verticales: claro|oscuro da un número grande; zona pareja da 0.")
    capsula(d, 3, "Nuestra red convolucional", [
        Runs([B("Recortes: "), ("todos los 3 × 3 como filas de 9 → un solo @.", {})]),
        Runs([B("Max-pooling 2 × 2: "), ("el máximo de cada cuadrito; tolera movimientos chicos.", {})])],
        derecha="R = recortes(imgs)\nZ = R @ red['F'] + red['bf']\nA = relu(Z)\nM = max_pool(A)\nplano = M.reshape(n, -1)\nP = softmax(plano @ red['W'] + red['b'])",
        formula="28² → 8 filtros → 26²×8\n→ pool → 13²×8 → 10")
    paso(d, 3, "armar y entrenar la red", "P7 · Ejercicio 2 y sección 5 · 20 min",
         [("Ej. 2", "el pase hacia adelante (Z, A, P)"), ("Entrenar", "~1 minuto con 20 000 imágenes")],
         "época 3: precisión en el examen 97.11%\nRed convolucional · originales: 97.1%   movidas: 23.2%",
         "Mientras entrena: solo el ganador del pooling recibe culpa; el filtro suma su pendiente de las 676 posiciones.")
    descanso(d, "el truco de los profesionales")
    capsula(d, 2, "¿Y si le enseñamos ejemplos movidos?", [
        "Mejoró un poco, pero no alcanza: la capa final todavía aprende posiciones.",
        Runs([B("Aumento de datos: "), ("fabricar ejemplos nuevos moviendo los que ya hay.", {})]),
        "¿Qué aumento NO sirve? Voltear: un 2 volteado ya no es un 2."],
        derecha="dy, dx = rng.integers(-3, 4, size=2)\nsalida[i] = np.roll(img, (dy, dx), axis=(0, 1))")
    s = d.slide(notes="Ejercicio 3 del notebook y comparación final.")
    title(s, "Paso 4 · Aumento de datos", "P7 · Ejercicio 3 · 20 min")
    table(s, LM, 1.95, CW, [["Red", "Originales", "Movidas 3 px"], ["Densa (Clase 6)", "97.6 %", "17 %"],
                            ["Convolucional", "97 %", "23 %"], ["Convolucional + aumento de datos", "94 %", "81 %"]],
          21, [6.83, 2.5, 2.5], 0.72, highlight=[3], align=[None, PP_ALIGN.CENTER, PP_ALIGN.CENTER])
    text(s, LM, 5.1, CW, 1.0, "Perdió un poquito con las originales y ganó muchísimo con las movidas.", 21, ORANGE, True)
    s = d.slide(True, notes="Que identifiquen cada línea con lo que programaron.")
    title(s, "Lo mismo, en la vida real (PyTorch)", "Cierre del curso")
    code(s, LM, 1.9, 7.4, 4.2, "red = nn.Sequential(\n    nn.Conv2d(1, 8, 3), nn.ReLU(), nn.MaxPool2d(2),\n    nn.Flatten(), nn.Linear(1352, 10))\n"
                               "opt = torch.optim.SGD(red.parameters(),\n                      lr=0.05, momentum=0.9)\nfor x, y in datos:\n"
                               "    error = F.cross_entropy(red(x), y)\n    opt.zero_grad(); error.backward()\n    opt.step()", 15)
    text(s, 8.5, 1.9, 4.08, 4.3, ["Conv2d → tus filtros", "cross_entropy → tu softmax + error", "backward() → tu retropropagación",
                                  "SGD(momentum) → tu momentum",
                                  ("La diferencia: tú sabes qué pasa dentro de cada línea.", {"color": AMBER, "bold": True})],
         18, SOFT, space=10)
    mapa(d, 0, notes="El recorrido completo. Que cada uno diga qué pieza le costó más.")
    s = d.slide(notes="Proyecto final en parejas: elegir una mejora, medirla y presentarla en 3 minutos.")
    title(s, "Proyecto final: mejora tu red", "En parejas · 3 minutos de presentación")
    for k, (h, b) in enumerate([("Más capas", "dos capas ocultas, o una segunda capa convolucional"),
                                ("Optimizador", "momentum + decaimiento juntos"),
                                ("Más aumento", "rotaciones pequeñas, trazo más grueso"),
                                ("Otros datos", "Fashion-MNIST: ropa en vez de dígitos")]):
        card(s, LM + k * 2.98, 1.95, 2.83, 3.3, h, b, [BLUE, ORANGE, BLUE, ORANGE][k], size=17, head_size=20)
    text(s, LM, 5.6, CW, 0.8, "Regla: medir antes y después, con los mismos datos de prueba.", 21, ORANGE, True)
    return d


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "entregables"
    os.makedirs(out, exist_ok=True)
    figuras()
    for name, fn in [("Clase1_Diapositivas", clase1), ("Clase2_Diapositivas", clase2),
                     ("Clase3_Diapositivas", clase3), ("Clase4_Diapositivas", clase4),
                     ("Clase5_Diapositivas", clase5), ("Clase6_Diapositivas", clase6),
                     ("Clase7_Diapositivas", clase7)]:
        path = os.path.join(out, name + ".pptx")
        print(path, fn().save(path), "diapositivas")
