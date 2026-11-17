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


BOOT = "from digitos import cargar_mnist, mostrar, ok"


# ================================================================ CLASE 1
def clase1():
    d = Deck("Introducción a las Redes Neuronales  ·  Clase 1")
    cover(d, "CLASE 1  ·  EL PROYECTO", "Vamos a construir", "una IA que lee números",
          "Hoy: instalar, conocer los datos y una primera IA… sin neuronas",
          "Antes de hablar: abre dibujar.py (Parte A.5 de la guía) y pide a un alumno que dibuje un número.")
    s = problema(d, "La demo", "Dibuja un número.\nLa red lo adivina.",
                 ["Esto lo van a programar ustedes, línea por línea, en Python y NumPy.",
                  "Sin librerías mágicas. En 7 clases."],
                 "Haz la demo en vivo con dibujar.py. Luego pregunta: ¿cómo le explicarían a una computadora qué es un 7?")
    concepto(d, "¿Cómo le explicas a una computadora qué es un 7?", "Reglas vs ejemplos",
             ["Con reglas: «una raya arriba y una diagonal»…",
              "…¿y el 7 con rayita? ¿el inclinado? ¿el mal hecho?",
              "Las reglas no escalan.",
              Runs([B("Aprendizaje automático: "), ("aprender de ejemplos con la respuesta correcta.", {})])],
             formula="ejemplos + respuestas\n→ la máquina saca la regla",
             notes="Deja que propongan reglas y muéstrales en el pizarrón cómo fallan. Samuel (1959): «capacidad de aprender "
                   "sin ser programado explícitamente».")
    mapa(d, 1)
    agenda(d, [["0:00", "Demo y cómo es el curso"], ["0:15", "Instalación y verificación"], ["0:55", "Descanso"],
               ["1:05", "IA, aprendizaje automático y datos: lo mínimo"], ["1:20", "Práctica: conocer los datos (P1)"],
               ["1:40", "Práctica: la IA de plantillas y la precisión (P1)"], ["2:15", "Puesta en común y cierre"]],
          highlight=[5])
    s = d.slide(notes="Sigue la Parte A de la guía. Quien se trabe más de 10 min, sigue en Colab.")
    title(s, "Dos caminos para trabajar", "Instalación")
    card(s, LM, 1.95, 5.8, 3.9, "Colab (sin instalar)",
         bullets(["colab.research.google.com", "Archivo → Abrir cuaderno → GitHub", "datahuba/curso-redes-neuronales",
                  "proyecto/P1_conocer_los_datos.ipynb"]), BLUE, size=17)
    card(s, LM + 6.03, 1.95, 5.8, 3.9, "Tu computadora (recomendado)",
         bullets(["Anaconda + Git + VS Code", "conda create --name nni python=3.11",
                  "git clone …/curso-redes-neuronales", "pip install -r requirements.txt"]), ORANGE, size=17)
    s = d.slide(True, notes="La verificación: abrir P1 con el kernel nni y ejecutar la primera celda.")
    title(s, "Verificación final")
    code(s, LM, 1.9, 7.0, 2.6, "cd ~\\projects\\curso-redes-neuronales\nconda activate nni\ngit pull\n"
                                "# VS Code → proyecto/P1_conocer_los_datos.ipynb\n# kernel: nni → Shift + Enter", 18)
    text(s, 8.1, 1.9, 4.48, 3.0, ["OK: La primera celda corre sin errores.", "OK: Descarga MNIST (11 MB, solo una vez).",
                                  ("¿Problemas? → Colab, y lo arreglamos después.", {"color": AMBER})], 19, SOFT, space=12)
    descanso(d, "los datos")
    concepto(d, "Lo mínimo de teoría", "Para entender el proyecto",
             [Runs([B("IA: "), ("máquinas que hacen tareas «inteligentes».", {})]),
              Runs([B("Aprendizaje automático: "), ("aprender de ejemplos.", {})]),
              Runs([B("Supervisado: "), ("cada ejemplo trae su respuesta (imagen + «es un 7»).", {})]),
              Runs([B("Entrenamiento / prueba: "), ("se aprende con unos datos y se evalúa con otros.", {})])],
             formula="60 000 para aprender\n10 000 para el examen",
             remate="Si el examen trae las preguntas de la práctica, no sabes si entendió o memorizó.",
             notes="Solo nombra no supervisado y por refuerzo. El resto de la teoría llega cuando el proyecto la pida.")
    s = d.slide(notes="Pide que encuentren el 5 dentro de los números. 0 = negro, 255 = blanco.")
    title(s, "Una imagen es una tabla de números", "Los datos: MNIST")
    import numpy as np
    sys.path.insert(0, os.path.join(RAIZ, "proyecto"))
    from digitos import cargar_mnist
    X0 = cargar_mnist()[0][0]
    grid(s, LM, 1.85, 0.34, X0[6:20, 9:23].tolist(), 8, shade=True)
    foto(s, "mnist.png", 6.0, 1.9, w=6.58)
    text(s, 6.0, 4.6, 6.58, 1.5, ["28 × 28 = 784 números entre 0 y 255.",
                                  ("Para la red: una fila de 784 números entre 0 y 1.", {"bold": True, "color": ORANGE})],
         19, GRAY, space=8)
    practica(d, "P1 · conocer los datos", "Secciones 1 y 2 · 20 min",
             [("Ej. 1", "¿cuántos ejemplos hay de cada dígito?"), ("Ej. 2", "aplanar a 784 y dividir entre 255")],
             "cuantos = np.bincount(y_train)\nX = X_train.reshape(60000, 784) / 255\n\n# OK: las imágenes son filas de 784\n"
             "# OK: los valores van de 0 a 1",
             "Las celdas con ... son tuyas. Después de cada ejercicio, la comprobación dice OK: o X con una pista.",
             notes="Error típico: reshape(784) sin la cantidad de imágenes.")
    figura(d, "Primera IA: el promedio de cada número", "Plantillas", "plantillas.png",
           [Runs([B("Adivinar = "), ("¿a qué plantilla se parece más?  "),
                  ("distancia = ((plantillas − x)²).sum(axis=1) → argmin", {"font": MONO})]),
            ("Nadie programó qué es un 3: las plantillas salen de los datos.", {"bold": True, "color": ORANGE})],
           "Antes de ejecutar, pregunta: si promedio los 6 000 tres, ¿qué saldrá?", h=1.6)
    practica(d, "P1 · la IA de plantillas", "Secciones 3 y 4 · 35 min",
             [("Ej. 3", "plantilla de cada dígito: X[y_train == d].mean(axis=0)"),
              ("Ej. 4", "predecir(x): la plantilla más cercana")],
             "predicciones = np.array([predecir(x) for x in Xt])\nprecision = (predicciones == y_test).mean()\n\n"
             "# Precisión: 82.0%",
             "Mira los errores: ¿tú también los confundirías?", notes="Mirar los errores juntos es lo más valioso de la clase.")
    resultado(d, "82 %", "sin una sola neurona", "Pero las plantillas nunca cambian: si se equivocan, no aprenden nada.",
              "¿Es bueno? Al azar sería 10 %. Pero 1 de cada 5 mal es mucho para leer cheques.")
    cierre(d, ["Vamos a construir un reconocedor de dígitos, pieza por pieza.",
               "Una imagen es una tabla de números → una fila de 784.",
               "Aprender de datos + medir con datos que no vio (precisión)."],
           "Próxima clase: una neurona que corrige sus pesos cuando se equivoca.",
           "terminar P1. Desafío: ¿y si usas el producto punto (plantillas @ x) con argmax?",
           "introducción del libro del Dr. Irving Vasquez (opcional).", "Vocabulario: dato, etiqueta, entrenamiento, prueba, precisión.")
    return d


# ================================================================ CLASE 2
def clase2():
    d = Deck("Introducción a las Redes Neuronales  ·  Clase 2")
    cover(d, "CLASE 2  ·  UNA NEURONA", "Una neurona que", "aprende de sus errores",
          "El perceptrón: de pesos a mano a pesos aprendidos", "Repaso: 82 % con plantillas que nunca cambian.")
    problema(d, "El problema", "Las plantillas se equivocan…\ny no aprenden nada.",
             ["Queremos algo que se corrija solo.", "Empecemos fácil: ¿esta imagen es un 0 o un 1?"],
             "Pregunta: ¿cuánto acertaban las plantillas? ¿Qué pasaba cuando se equivocaban?")
    mapa(d, 2)
    agenda(d, [["0:00", "Repaso y problema"], ["0:10", "¿Qué hace una neurona?"], ["0:25", "Práctica: compuerta AND a mano"],
               ["0:40", "Práctica: los datos 0/1 y la neurona"], ["1:00", "Descanso"], ["1:10", "La regla de Rosenblatt"],
               ["1:30", "Práctica: entrenar y mirar los pesos"], ["1:55", "Desafío 3 vs 5"], ["2:20", "Cierre"]],
          highlight=[6])
    concepto(d, "¿Qué hace una neurona?", "Suma ponderada + decisión",
             ["Recibe entradas (los 784 píxeles).", Runs([B("Pesos w: "), ("cuánto importa cada entrada (pueden ser negativos).", {})]),
              Runs([B("Sesgo b: "), ("qué tan fácil es decir que sí.", {})]),
              Runs([B("Decide: "), ("1 si la suma pasa de 0; si no, 0.", {})])],
             "salida = (x @ w + b > 0).astype(int)\n\n# @ = multiplicar casilla por casilla\n#     y sumar todo",
             formula="x₁w₁ + x₂w₂ + … + b > 0 ?",
             notes="Analogía: decidir si vas a un partido. McCulloch y Pitts (1943): pesos fijos. Rosenblatt (1958): aprenderlos.")
    practica(d, "P2 · compuerta AND a mano", "Sección 1 · 15 min",
             [("Calentamiento", "busca w y b para que solo [1, 1] dé 1")],
             "entradas = [[0,0], [0,1], [1,0], [1,1]]\n# salida esperada:  0, 0, 0, 1\nw_and = np.array([..., ...])\nb_and = ...",
             "¿Y la compuerta OR? ¿Hay una sola respuesta correcta?",
             notes="5 minutos sin pistas. Una solución: pesos 1, 1 y sesgo −1.5. OR: sesgo −0.5. Infinitas respuestas → se puede aprender.")
    practica(d, "P2 · la neurona con imágenes", "Sección 2 y Ejercicio 1 · 20 min",
             [("Datos", "solo ceros y unos: y = 1 si es un 1"), ("Ej. 1", "neurona(x, w, b) para muchas imágenes a la vez")],
             "def neurona(x, w, b):\n    return ...\n\n# pesos al azar → ~50 %: tirar una moneda",
             "Truco: (condición).astype(int) funciona con una imagen o con miles.",
             notes="Error típico: usar if, que falla con muchas imágenes.")
    descanso(d, "la regla de aprendizaje")
    concepto(d, "La regla de Rosenblatt", "Aprender de los errores",
             ["Acertó → no se toca nada.", "Dijo 0 y era 1 (error +1) → sube los pesos de los píxeles encendidos.",
              "Dijo 1 y era 0 (error −1) → bájalos.", Runs([B("η (eta): "), ("tamaño de cada corrección.", {})])],
             "x = [1, 0, 1]   w = [0, 0, 0]   b = 0\ny = 1  → dijo 0 → error = +1\nw = [0.1, 0, 0.1]   b = 0.1\n"
             "→ suma = 0.3 > 0 → dice 1 OK",
             formula="error = y − ŷ\nw ← w + η·error·x",
             notes="Haz el ejemplo de 3 píxeles en el pizarrón. Solo cambian los pesos de los píxeles encendidos.")
    practica(d, "P2 · entrenar", "Ejercicio 2 · 25 min",
             [("Ej. 2", "completa la corrección de w y de b"), ("Mira", "cómo bajan los errores por época")],
             "época 1: se equivocó 45 veces\népoca 2: se equivocó 24 veces\n...\nPrecisión en el examen: 99.81%",
             notes="Errores típicos: w = eta*error*xi (falta sumar el w anterior); usar y en lugar de yi.")
    s = d.slide(notes="Rojo en el centro (donde el 1 tiene tinta), azul en el anillo (donde el 0 tiene tinta).")
    title(s, "¿Qué aprendió? Los pesos como imagen")
    foto(s, "pesos_perceptron.png", LM, 1.8, h=4.3)
    text(s, 5.6, 2.0, 6.98, 4.0, bullets([Runs([C("Rojo", ORANGE), (": «si hay tinta acá, digo 1»", {})]),
                                          Runs([C("Azul", BLUE), (": «si hay tinta acá, digo 0»", {})]),
                                          "Nadie le dijo dónde mirar: lo sacó de los ejemplos."]), 21, GRAY, space=14)
    practica(d, "P2 · desafío 3 vs 5", "Sección 5 · 25 min",
             [("Cambia", "A, B = 3, 5 y ejecuta todo"), ("Observa", "¿los errores por época llegan a cero?")],
             "época 1: se equivocó 823 veces\népoca 2: se equivocó 651 veces\népoca 3: se equivocó 636 veces\n# nunca se calma",
             "La regla solo sabe si acertó, no cuánto se equivocó.",
             notes="Precisión ~95 % pero no se estabiliza. ¿Por qué? Mismo empujón por un error mínimo que por uno enorme.")
    cierre(d, ["Neurona = suma ponderada + decisión.", "Aprender = corregir los pesos cuando se equivoca.",
               "Límite: solo dice 0/1 y no mide cuánto se equivocó."],
           "Próxima clase: «es un 5 con 80 % de seguridad» y bajar el error poco a poco.",
           "terminar P2; probar 3 vs 5 con epocas=10.", "refuerzo: notebooks 1_01, 1_02, 1_03_1 y 1_03_2 (opcional).",
           "Cierra con la pregunta: ¿cómo sabría cuánto se equivocó?")
    return d


# ================================================================ CLASE 3
def clase3():
    d = Deck("Introducción a las Redes Neuronales  ·  Clase 3")
    cover(d, "CLASE 3  ·  DESCENSO POR GRADIENTE", "Aprender bajando", "la montaña",
          "Sigmoide, error medible y descenso por gradiente", "Repaso: el perceptrón con 3 vs 5 nunca se calma.")
    problema(d, "El problema", "El perceptrón no sabe\ncuánto se equivocó.",
             ["Un 5 dudoso y un 5 clarísimo mal clasificados reciben el mismo empujón.",
              "Hoy: una salida suave y un error que se pueda medir y bajar."],
             "Muestra los errores por época del perceptrón con 3 vs 5.")
    mapa(d, 3)
    agenda(d, [["0:00", "Repaso y problema"], ["0:10", "La sigmoide"], ["0:30", "La montaña con niebla"],
               ["0:50", "Práctica: descenso con un número"], ["1:10", "Descanso"], ["1:20", "Error medible y pendiente"],
               ["1:35", "Práctica: entrenar 3 vs 5"], ["2:05", "¿Cuándo duda?"], ["2:20", "Cierre"]], highlight=[7])
    concepto(d, "La sigmoide: de «sí/no» a «qué tan seguro»", "Ejercicio 1",
             ["Un escalón suavizado.", "Muy negativo → 0 · muy positivo → 1 · cero → 0.5.",
              "La salida se lee como probabilidad: 0.8 = «80 % seguro de que es un 5».",
              "Suave → si muevo un poco un peso, la salida cambia un poco."],
             formula="σ(z) = 1 / (1 + e⁻ᶻ)", fig="sigmoide.png", notes="Ejercicio 1 del notebook: escribirla con np.exp.")
    concepto(d, "La montaña con niebla", "Descenso por gradiente",
             ["Quieres llegar al fondo del valle: el error mínimo.", "Solo sientes la pendiente bajo tus pies.",
              "Da un paso cuesta abajo, vuelve a sentir, repite.",
              Runs([B("Pendiente = derivada: "), ("hacia dónde sube y qué tan empinado.", {})])],
             "E(w) = (w − 3)²       # error inventado\npendiente = 2·(w − 3)\n\n# w < 3 → pendiente negativa → ir a la derecha",
             formula="w ← w − η · pendiente", notes="Dibuja la parábola. En el fondo la pendiente es 0.")
    figura(d, "La tasa de aprendizaje lo es todo", "Práctica · sección 2", "descenso.png",
           [Runs([B("0.1: "), ("baja suave.   ", {}), B("0.5: "), ("llega de un salto.   ", {}), B("1.05: "),
                  ("rebota y se aleja (diverge).", {})]),
            ("Prueba 0.01 y 0.9. ¿Qué pasa?", {"bold": True, "color": ORANGE})],
           "Ejercicio 2. La tasa de aprendizaje es la decisión más importante al entrenar.", h=3.0)
    descanso(d, "la neurona que aprende con gradiente")
    concepto(d, "La pendiente de la neurona", "Error medible",
             [Runs([B("Entropía cruzada: "), ("castiga estar muy seguro y equivocado.", {})]),
              "Un solo número que queremos bajar.",
              Runs([B("Léanla: "), ("(lo que dijo − lo correcto) × entrada.", {})]),
              "¡Casi Rosenblatt! Pero p − y dice cuánto se equivocó."],
             "p = sigmoide(X @ w + b)\ngrad_w = X.T @ (p - y) / len(X)\ngrad_b = np.mean(p - y)\nw, b = w - eta*grad_w, b - eta*grad_b",
             formula="grad_w = Xᵀ(p − y) / n",
             notes="Para curiosos: la derivada de la sigmoide se cancela con la del logaritmo. Se ve en la Clase 5.")
    practica(d, "P3 · entrenar 3 vs 5", "Ejercicio 3 · 30 min",
             [("Ej. 3", "predecir, calcular pendientes, dar el paso"), ("Mira", "la curva de aprendizaje")],
             "# La curva baja suave, sin saltos\nPrecisión 3 vs 5: 96.1%",
             "¿Por qué baja rápido al principio y lento al final? Prueba eta = 5.",
             notes="Errores típicos: X @ (p - y) sin .T; no dividir por len(X).")
    concepto(d, "Ahora sabe cuándo duda", "Sección 4",
             ["Las imágenes con probabilidad cerca de 50 %…", "…también harían dudar a una persona.",
              "La red sabe cuándo no sabe: una ventaja enorme."],
             "dudas = np.argsort(np.abs(p_test - 0.5))[:10]\nmostrar(Xt[dudas], ...)",
             notes="Muestra las imágenes dudosas del resuelto.")
    cierre(d, ["Sigmoide → probabilidades.", "Error medible + descenso por gradiente → aprender poco a poco.",
               "La curva de aprendizaje se mira siempre."],
           "Próxima clase: 10 neuronas, una por dígito… y van a dibujar sus números.",
           "terminar P3; probar 4 vs 9 y 1 vs 7: ¿cuál es el más difícil?", "refuerzo: notebooks 1_04 y 1_05 (opcional).",
           "Pregunta de salida: ¿qué pasa si eta es demasiado grande?")
    return d


# ================================================================ CLASE 4
def clase4():
    d = Deck("Introducción a las Redes Neuronales  ·  Clase 4")
    cover(d, "CLASE 4  ·  DIEZ NEURONAS", "Del 0 al 9", "¡y a dibujar!",
          "One-hot, softmax, mini-lotes y tu primera red que lee tus números", "Hoy cada alumno dibuja sus números.")
    problema(d, "El problema", "Una neurona responde sí o no.\n¿Cómo reconozco 10 dígitos?",
             ["10 neuronas, una por dígito, mirando la misma imagen.", "Gana la más convencida."],
             "Deja que lo deduzcan antes de mostrar la respuesta.")
    mapa(d, 4)
    agenda(d, [["0:00", "Repaso y problema"], ["0:10", "One-hot y softmax"], ["0:35", "La tabla de pesos"],
               ["0:45", "Mini-lotes: entrenar"], ["1:10", "Descanso"], ["1:20", "¿Qué mira cada neurona? Confusión"],
               ["1:40", "¡A dibujar!"], ["2:10", "Puesta en común y cierre"]], highlight=[7])
    concepto(d, "One-hot y softmax", "Ejercicios 1 y 2",
             [Runs([B("One-hot: "), ("3 → [0,0,0,1,0,0,0,0,0,0]  =  np.eye(10)[y]", {})]),
              Runs([B("Softmax: "), ("10 puntajes → 10 probabilidades que suman 1.", {})]),
              "La exponencial hace todo positivo y exagera al ganador.",
              "Restar el máximo antes no cambia nada y evita números gigantes."],
             "E = np.exp(Z - Z.max(axis=1, keepdims=True))\nP = E / E.sum(axis=1, keepdims=True)\n\n"
             "# [2, 1, 0.1] → [0.66, 0.24, 0.10]",
             formula="pₖ = eᶻᵏ / Σ eᶻ", notes="Haz [2, 1, 0.1] en el pizarrón. Error típico: sum sin axis=1, keepdims=True.")
    concepto(d, "La tabla de pesos y la misma pendiente", "Nada nuevo, solo más columnas",
             [Runs([B("W: "), ("784 × 10, una columna por neurona.", {})]), "X @ W + b → 10 puntajes por imagen.",
              "La pendiente es la de la Clase 3: error × entrada."],
             "P = softmax(Xb @ W + b)\ngrad_W = Xb.T @ (P - Yb) / len(Xb)\ngrad_b = (P - Yb).mean(axis=0)",
             formula="grad_W = Xᵀ(P − Y) / n", notes="Destaca que la fórmula es idéntica a la de la Clase 3.")
    practica(d, "P4 · entrenar por mini-lotes", "Ejercicio 3 · 25 min",
             [("Idea", "no hace falta preguntar a 60 000 para corregir el rumbo: con 128 alcanza"),
              ("Ej. 3", "el paso dentro del ciclo de lotes")],
             "época 1: error 0.35\n...\népoca 5: error 0.27\nPrecisión en los 10 dígitos: 92.2%",
             "Una época ≈ 470 pasos. Mezclar en cada época.", notes="Recuerda: 82 % plantillas → 92 %.")
    descanso(d, "qué mira cada neurona… y a dibujar")
    figura(d, "¿Qué mira cada neurona?", "Pesos como imágenes", "pesos10.png",
           ["Fantasmas de cada dígito: compáralos con las plantillas de la Clase 1.",
            ("Ahora hay azul: lo que resta.", {"bold": True, "color": ORANGE})],
           "Luego la matriz de confusión: que encuentren las confusiones más grandes (4↔9, 3↔5, 7↔9).", h=1.6)
    s = d.slide(True, notes="Terminal en la carpeta proyecto/. En Colab: Paint + mi_numero.png + última celda.")
    title(s, "¡A dibujar!")
    code(s, LM, 1.9, 6.2, 2.4, "# en el notebook:\nguardar_pesos(W1=W, b1=b)\n\n# en una terminal, carpeta proyecto/:\npython dibujar.py", 18)
    text(s, 7.3, 1.9, 5.28, 3.6, ["Clic izquierdo: dibujar.", "Clic derecho: borrar.",
                                  ("Mini-competencia: ¿quién engaña a la red con un número que una persona leería?",
                                   {"color": AMBER, "bold": True}),
                                  ("Colab: dibuja en Paint, sube mi_numero.png y usa la última celda.", {"color": MUTED})],
         19, SOFT, space=12)
    resultado(d, "92 %", "y ya lee tus dibujos", "Pero cada neurona separa con una línea recta: entrenar más no ayuda.",
              "Pide que anoten qué dibujos la engañan: los usaremos en la Clase 5.")
    cierre(d, ["10 neuronas + softmax = clasificador de 10 clases.", "Mini-lotes = entrenar rápido.",
               "Límite: modelo lineal, se queda en ~92 %."],
           "Próxima clase: una capa oculta → de 92 % a 97 %.",
           "terminar P4 y traer 3 dibujos que engañan a la red.", "refuerzo: notebooks 1_06, 1_07 y 1_08 (opcional).",
           "¿Con qué dibujos falla más?")
    return d


# ================================================================ CLASE 5
def clase5():
    d = Deck("Introducción a las Redes Neuronales  ·  Clase 5")
    cover(d, "CLASE 5  ·  RED MULTICAPA", "La red de verdad", "capa oculta y retropropagación",
          "De 92 % a 97 %", "Empieza mostrando los dibujos que engañaron a la red de la Clase 4.")
    problema(d, "El problema", "Entrenar más no ayuda:\nse queda en 92 %.",
             ["Cada neurona solo puede trazar una línea recta.", "El modelo es demasiado simple."],
             "Pregunta: si entreno más épocas, ¿mejora?")
    mapa(d, 5)
    agenda(d, [["0:00", "Repaso: el techo del 92 %"], ["0:10", "La idea de la capa oculta"],
               ["0:25", "ReLU y pase hacia adelante"], ["0:50", "Descanso"], ["1:00", "Retropropagación"],
               ["1:25", "Práctica: retropropagación y verificación"], ["1:50", "Entrenar y dibujar"],
               ["2:15", "Experimentos y cierre"]], highlight=[5])
    s = d.slide(notes="Analogía de la fábrica: 128 inspectores detectan rasgos; el jefe decide con sus informes. Nadie les dice qué buscar.")
    title(s, "La capa oculta: inspectores de rasgos", "La idea")
    red(s, 1.4, 2.0, 5.0, 3.4, [5, 4, 3], ["imagen (784)", "oculta (128)", "salida (10)"])
    text(s, 7.6, 2.0, 4.98, 4.3, bullets(["Cada neurona oculta aprende un rasgo: un círculo arriba, una raya…",
                                          "La salida decide con esos rasgos, no con píxeles sueltos.",
                                          Runs([B("Nadie les dice qué buscar: "), ("lo aprenden.", {})])]), 19, GRAY, space=14)
    concepto(d, "ReLU y pase hacia adelante", "Ejercicios 1 y 2",
             [Runs([B("ReLU = max(0, z): "), ("deja pasar lo positivo, apaga lo negativo.", {})]),
              "Sin activación, dos capas = una sola (volvemos a lo lineal).",
              "Tamaños: (n×784)·(784×128) → (n×128)·(128×10) → (n×10).",
              "Pesos iniciales al azar: si todos son 0, todos aprenden lo mismo."],
             "Z1 = X @ W1 + b1\nA1 = relu(Z1)\nP  = softmax(A1 @ W2 + b2)",
             formula="784 → 128 → 10", notes="Regla de tamaños: los números de adentro deben coincidir.")
    descanso(d, "retropropagación")
    s = d.slide(notes="El corazón del curso. Primero la idea sin fórmulas: la culpa de cada inspector depende de cuánto pesaba su informe "
                      "y de si estaba encendido. Luego los 5 pasos, marcando la red hacia atrás.")
    title(s, "Retropropagación: repartir la culpa hacia atrás", "El corazón del curso")
    table(s, LM, 1.85, CW, [["Paso", "Código", "En palabras"],
                            ["1", "dZ2 = (P - Y) / n", "error de la salida (como en la Clase 4)"],
                            ["2", "dW2 = A1.T @ dZ2", "pendiente capa 2: error × entrada"],
                            ["3", "dA1 = dZ2 @ W2.T", "culpa de cada neurona oculta"],
                            ["4", "dZ1 = dA1 * (Z1 > 0)", "si estaba apagada, culpa 0"],
                            ["5", "dW1 = X.T @ dZ1", "pendiente capa 1: ¡la misma receta!"]],
          18, [1.0, 4.6, 6.23], 0.58, highlight=[3])
    text(s, LM, 5.55, CW, 0.8, "No hay matemática nueva: la regla de la cadena, capa por capa.", 21, ORANGE, True)
    practica(d, "P5 · retropropagación", "Ejercicio 3 · 25 min",
             [("Ej. 3", "los 5 pasos, una línea cada uno"), ("Verifica", "mover un peso 0.00001 y medir")],
             "W1  tu función: -0.001241\n    a mano:     -0.001241\nOK: la pendiente de W1 es correcta\n"
             "W2  tu función:  0.000960\n    a mano:      0.000960\nOK: la pendiente de W2 es correcta",
             "Así depuran redes los profesionales.",
             notes="Errores típicos: A1 @ dZ2 sin .T; dZ2 @ W2 sin .T; dZ1 = dA1 * Z1 (debe ser la máscara Z1 > 0).")
    practica(d, "P5 · entrenar y dibujar", "Secciones 5 y 6 · 25 min",
             [("Entrenar", "el mismo ciclo de la Clase 4"), ("Dibujar", "guardar_pesos(**red) → python dibujar.py")],
             "época 1: precisión 93.99%\népoca 3: precisión 96.38%\népoca 5: precisión 97.20%",
             "Prueba los dibujos que engañaban a la red de la Clase 4.")
    resultado(d, "97 %", "con una capa oculta", "92 % → 97 %: de 8 errores cada 100 a 3.", "Experimentos en grupos (sección 7).")
    cierre(d, ["Capa oculta = rasgos aprendidos.", "Retropropagación = repartir el error hacia atrás, misma receta.",
               "Verificar pendientes numéricamente."],
           "Próxima clase: entrenar más rápido (optimizadores).",
           "terminar P5 + un experimento (ocultas, eta o sigmoide).", "refuerzo: notebooks 1_09, 1_10 y 1_11 con XOR (opcional).",
           "Pregunta: ¿por qué hace falta la ReLU?")
    return d


# ================================================================ CLASE 6
def clase6():
    d = Deck("Introducción a las Redes Neuronales  ·  Clase 6")
    cover(d, "CLASE 6  ·  OPTIMIZADORES", "Entrenar más rápido", "y mejor",
          "Momentum y decaimiento de la tasa, en una carrera", "La red no cambia hoy: solo cómo bajamos la montaña.")
    problema(d, "El problema", "eta chico: una eternidad.\neta grande: rebota.",
             ["En un valle alargado, la pendiente apunta a las paredes → zigzag.", "Así son los errores de las redes reales."],
             "Dibuja un valle alargado (canaleta) y el zigzag.")
    mapa(d, 6)
    agenda(d, [["0:00", "Repaso y problema"], ["0:10", "Paso 0: tus funciones de la Clase 5"], ["0:20", "La pista y SGD"],
               ["0:30", "Momentum"], ["0:55", "Descanso"], ["1:05", "Decaimiento de la tasa"], ["1:20", "¡La carrera!"],
               ["1:50", "La red definitiva + dibujar"], ["2:05", "Cierre: Adam"]], highlight=[7])
    concepto(d, "Momentum: la pelota que rueda", "Ejercicio 1",
             ["Si la pendiente apunta siempre al mismo lado → acelera.", "Si cambia de lado (zigzag) → se cancela, se suaviza.",
              Runs([B("β = 0.9: "), ("recuerdo el 90 % de mi velocidad anterior.", {})]),
              "Pendiente constante: hasta 10 veces más rápido que SGD."],
             "v = memoria.get(k, 0)\nv = beta * v - eta * g[k]\nmemoria[k] = v\nred[k] += v",
             formula="v ← βv − η·pendiente\npeso ← peso + v", notes="Velocidad con pendiente 1 y eta 0.01: 0.01, 0.019, 0.027… → 0.1.")
    descanso(d, "decaimiento y la carrera")
    concepto(d, "Decaimiento de la tasa", "Ejercicio 2",
             ["Como estacionar: lejos, rápido; cerca, despacio.", "Pasos grandes al principio, chicos al final.",
              "eta0 = 0.3, k = 1 → 0.3, 0.15, 0.1, 0.075…"],
             "eta = eta0 / (1 + k * epoca)", formula="η = η₀ / (1 + k·época)")
    s = d.slide(notes="Resultados reales con 20 000 imágenes y 5 épocas. Pregunta: ¿por qué momentum le gana a SGD con el mismo eta? "
                      "¿No sería igual SGD con eta grande? Que prueben 0.5 y 2.0.")
    title(s, "¡La carrera!", "Misma red, distinto optimizador")
    table(s, LM, 1.95, CW, [["Corredor", "Error final", "Precisión"], ["SGD (eta 0.01)", "0.38", "90 %"],
                            ["Momentum (eta 0.01)", "0.15", "95 %"], ["Decaimiento (eta0 0.3)", "0.11", "96 %"]],
          22, [6.83, 2.5, 2.5], 0.75, highlight=[2], align=[None, PP_ALIGN.CENTER, PP_ALIGN.CENTER])
    text(s, LM, 5.2, CW, 1.0, "Momentum da velocidad sin volverse inestable.", 22, ORANGE, True)
    practica(d, "P6 · experimentos y red definitiva", "Secciones 6 y 7 · 45 min",
             [("Prueba", "SGD con eta 0.5 y 2.0; momentum con beta 0.99"),
              ("Definitiva", "momentum, 60 000 imágenes, 5 épocas")],
             "Precisión de la red definitiva: 97.64%\nOK: la red definitiva supera el 97 %\npython dibujar.py",
             "Cada grupo cuenta su experimento en 1 minuto.")
    cierre(d, ["Optimizador = cómo bajar la montaña; red y pendientes no cambian.",
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
          "Filtros convolucionales, pooling, aumento de datos… y el cierre del proyecto",
          "Antes de ejecutar la sección 1, que apuesten cuánto bajará la precisión.")
    figura(d, "Mueve el dibujo 3 píxeles…", "El experimento", "movidas.png",
           [Runs([("Tu red densa: ", {}), C("97.6 %", BLUE), (" con las originales → ", {}), C("17 %", ORANGE),
                  (" con las movidas.", {})]),
            ("Aprendió dónde hay tinta, no qué forma tiene el número.", {"bold": True, "color": ORANGE})],
           "Cada píxel tiene su propio peso: la red no sabe que los vecinos están relacionados.", h=2.9)
    mapa(d, 7)
    agenda(d, [["0:00", "El experimento que rompe la red"], ["0:15", "La convolución"],
               ["0:40", "Versión rápida y red convolucional"], ["1:05", "Descanso"], ["1:15", "Entrenar"],
               ["1:30", "Aumento de datos"], ["1:55", "Los filtros aprendidos"], ["2:05", "Cierre del curso"]], highlight=[2])
    concepto(d, "La convolución: una lupa que recorre la imagen", "Ejercicio 1",
             ["Un filtro 3 × 3 busca una sola cosa (un borde, una curva).",
              "En cada posición: multiplicar casilla por casilla y sumar.",
              Runs([B("El mismo filtro en todas partes: "), ("lo detecta arriba o abajo.", {})]),
              "9 pesos en vez de 784, y se aprenden."],
             fig="filtros.png", formula="salida[i, j] = (img[i:i+3, j:j+3] * filtro).sum()", ancho=5.6,
             notes="Ejemplo en el pizarrón con el filtro de bordes verticales: claro|oscuro da un número grande; zona pareja da 0.")
    concepto(d, "Nuestra red convolucional", "Ejercicio 2",
             [Runs([B("Recortes: "), ("todos los 3 × 3 como filas de 9 → un solo @.", {})]),
              Runs([B("Max-pooling 2 × 2: "), ("el máximo de cada cuadrito; tolera movimientos chicos.", {})]),
              "Retropropagación: solo el ganador del pooling recibe culpa; el filtro suma su pendiente de las 676 posiciones."],
             "R = recortes(imgs)\nZ = R @ red['F'] + red['bf']\nA = relu(Z)\nM = max_pool(A)\nplano = M.reshape(n, -1)\nP = softmax(plano @ red['W'] + red['b'])",
             formula="28² → 8 filtros → 26²×8\n→ pool → 13²×8 → 10",
             notes="Mientras entrena (~1 min) explica los dos detalles nuevos de la retropropagación.")
    descanso(d, "entrenar y el truco de los profesionales")
    s = d.slide(notes="Pregunta: si quieres que no le importe la posición, ¿qué ejemplos le mostrarías? → ejemplos movidos. "
                      "¿Qué aumento NO tiene sentido? Voltear horizontalmente: un 2 volteado ya no es un 2.")
    title(s, "Aumento de datos: enseñarle ejemplos movidos", "Ejercicio 3")
    table(s, LM, 1.95, CW, [["Red", "Originales", "Movidas 3 px"], ["Densa (Clase 6)", "97.6 %", "17 %"],
                            ["Convolucional", "97 %", "23 %"], ["Convolucional + aumento de datos", "94 %", "81 %"]],
          21, [6.83, 2.5, 2.5], 0.72, highlight=[3], align=[None, PP_ALIGN.CENTER, PP_ALIGN.CENTER])
    code(s, LM, 5.05, 7.5, 1.2, "dy, dx = rng.integers(-3, 4, size=2)\nsalida[i] = np.roll(img, (dy, dx), axis=(0, 1))", 15)
    text(s, 8.5, 5.05, 4.08, 1.3, "No hacen falta datos nuevos: se fabrican.", 20, ORANGE, True)
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
