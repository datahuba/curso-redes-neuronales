"""Convierte guías Markdown a PDF (HTML con estilo + Chrome/Edge sin ventana).

Uso: python tools/md_to_pdf.py docs/GUIA.md entregables/Guia.pdf
Requiere: pip install markdown-it-py mdit-py-plugins  ·  Chrome o Edge instalado.
Las fórmulas $$...$$ se dibujan con KaTeX (necesita internet al convertir).
"""
import html
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin
from mdit_py_plugins.tasklists import tasklists_plugin

BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    shutil.which("chrome") or "", shutil.which("msedge") or "", shutil.which("chromium") or "",
]

CSS = """
@page { size: A4; margin: 18mm 16mm 18mm 16mm;
  @bottom-left { content: "Introducción a las Redes Neuronales"; font: 8.5pt 'Segoe UI', sans-serif; color: #8F9BB3; }
  @bottom-right { content: counter(page) " / " counter(pages); font: 8.5pt 'Segoe UI', sans-serif; color: #8F9BB3; } }
:root { --navy:#14213D; --orange:#C4621D; --blue:#2F6FB0; --gray:#4A5568; --band:#EFEBE1; --card:#FFFDF8; --border:#E2DED3; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 10.5pt; line-height: 1.5; color: #1F2937; margin: 0; }
h1 { color: var(--navy); font-size: 17pt; margin: 22pt 0 8pt; padding-bottom: 4pt; border-bottom: 2.5pt solid var(--orange);
     break-after: avoid; }
h1:first-of-type { font-size: 21pt; margin-top: 0; border-bottom: none; padding: 14pt 16pt; background: var(--navy);
     color: #F7F5EF; border-left: 6pt solid var(--orange); }
h2 { color: var(--navy); font-size: 13.5pt; margin: 16pt 0 6pt; break-after: avoid; }
h3 { color: var(--blue); font-size: 11.5pt; margin: 12pt 0 4pt; break-after: avoid; }
p { margin: 4pt 0 6pt; }
a { color: var(--blue); text-decoration: none; word-break: break-word; }
strong { color: var(--navy); }
hr { border: none; border-top: 1pt solid var(--border); margin: 14pt 0; }
ul, ol { margin: 3pt 0 6pt; padding-left: 20pt; }
li { margin: 2pt 0; }
li > p { margin: 2pt 0; }
code { font-family: Consolas, monospace; font-size: 9.5pt; background: var(--band); padding: 0.5pt 3pt; border-radius: 3pt;
       color: var(--navy); }
pre { background: #0D1629; color: #E6EAF2; padding: 8pt 11pt; border-radius: 5pt; break-inside: avoid; margin: 4pt 0 8pt;
      white-space: pre-wrap; word-break: break-word; }
pre code { background: none; color: inherit; padding: 0; font-size: 9.5pt; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0 10pt; font-size: 9.5pt; break-inside: auto; }
tr { break-inside: avoid; }
th { background: var(--navy); color: #F7F5EF; text-align: left; padding: 4pt 7pt; }
td { padding: 4pt 7pt; border-bottom: 0.75pt solid var(--border); vertical-align: top; }
tr:nth-child(even) td { background: #F7F5EF; }
blockquote { margin: 6pt 0; padding: 5pt 11pt; background: var(--card); border-left: 4pt solid var(--orange); color: var(--gray); }
blockquote p { margin: 2pt 0; }
.contains-task-list { list-style: none; padding-left: 6pt; }
.task-list-item input { margin-right: 6pt; }
.math.block { margin: 8pt 0; text-align: center; }
"""

TEMPLATE = """<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{title}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<style>{css}</style></head><body>{body}
<script>
document.querySelectorAll('.math').forEach(function (el) {{
  try {{ katex.render(el.textContent, el, {{displayMode: el.classList.contains('block'), throwOnError: false}}); }}
  catch (e) {{}}
}});
</script></body></html>"""


def render(md_text):
    md = MarkdownIt("commonmark", {"html": False, "linkify": False, "breaks": True}).enable("table").use(dollarmath_plugin).use(
        tasklists_plugin)
    return md.render(md_text)


def main(src, dst):
    text = pathlib.Path(src).read_text(encoding="utf-8")
    title = next((ln[2:].strip() for ln in text.splitlines() if ln.startswith("# ")), "Guía")
    page = TEMPLATE.format(title=html.escape(title), css=CSS, body=render(text))
    browser = next((b for b in BROWSERS if b and os.path.exists(b)), None)
    if not browser:
        sys.exit("No se encontró Chrome ni Edge.")
    with tempfile.TemporaryDirectory() as tmp:
        page_path = pathlib.Path(tmp, "guia.html")
        page_path.write_text(page, encoding="utf-8")
        out = os.path.abspath(dst)
        subprocess.run([browser, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        "--virtual-time-budget=20000", f"--user-data-dir={tmp}", f"--print-to-pdf={out}",
                        page_path.as_uri()], check=True, capture_output=True, timeout=120)
    print("PDF:", dst)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
