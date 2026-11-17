"""Dibuja un número con el mouse y mira qué dice TU red.

Uso (desde la carpeta proyecto/, después de guardar tus pesos en el notebook P4, P5 o P6):
    python dibujar.py              -> usa pesos.npz
    python dibujar.py otros.npz    -> usa otro archivo de pesos

Clic izquierdo: dibujar · Clic derecho o botón «Borrar»: empezar de nuevo.
(No funciona en Google Colab: allí dibuja en Paint, sube el PNG y usa leer_dibujo() en el notebook.)
"""
import os
import sys
import tkinter as tk

import numpy as np
from PIL import Image, ImageDraw

from digitos import AQUI, predecir_con_pesos, preparar_dibujo

TAM, GROSOR = 280, 22


def main():
    archivo = os.path.join(AQUI, sys.argv[1] if len(sys.argv) > 1 else "pesos.npz")
    if not os.path.exists(archivo):
        sys.exit(f"No encuentro {archivo}. Entrena tu red en el notebook y ejecuta guardar_pesos(...) primero.")
    pesos = dict(np.load(archivo))

    raiz = tk.Tk()
    raiz.title("¿Qué número es?")
    lienzo = tk.Canvas(raiz, width=TAM, height=TAM, bg="black", cursor="pencil")
    lienzo.grid(row=0, column=0, rowspan=2, padx=10, pady=10)
    texto = tk.Label(raiz, text="Dibuja un número", font=("Segoe UI", 40, "bold"), width=4)
    texto.grid(row=0, column=1, padx=10)
    barras = tk.Label(raiz, text="", font=("Consolas", 12), justify="left")
    barras.grid(row=1, column=1, padx=10, sticky="n")
    img = Image.new("L", (TAM, TAM), 0)
    pincel = ImageDraw.Draw(img)
    ultimo = [None]

    def adivinar():
        p = predecir_con_pesos(pesos, preparar_dibujo(img))[0]
        texto.config(text=str(p.argmax()))
        barras.config(text="\n".join(f"{d}  {'█' * int(p[d] * 20):<20} {p[d]:5.1%}" for d in range(10)))

    def trazo(e):
        if ultimo[0]:
            lienzo.create_line(*ultimo[0], e.x, e.y, fill="white", width=GROSOR, capstyle="round", smooth=True)
            pincel.line([ultimo[0], (e.x, e.y)], fill=255, width=GROSOR, joint="curve")
        r = GROSOR // 2
        pincel.ellipse([e.x - r, e.y - r, e.x + r, e.y + r], fill=255)
        ultimo[0] = (e.x, e.y)

    def soltar(_):
        ultimo[0] = None
        adivinar()

    def borrar(_=None):
        lienzo.delete("all")
        pincel.rectangle([0, 0, TAM, TAM], fill=0)
        texto.config(text="?")
        barras.config(text="")

    lienzo.bind("<B1-Motion>", trazo)
    lienzo.bind("<Button-1>", trazo)
    lienzo.bind("<ButtonRelease-1>", soltar)
    lienzo.bind("<Button-3>", borrar)
    tk.Button(raiz, text="Borrar", command=borrar, font=("Segoe UI", 14)).grid(row=2, column=0, pady=(0, 10))
    raiz.mainloop()


if __name__ == "__main__":
    main()
