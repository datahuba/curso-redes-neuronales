"""Servicio mínimo de registro y grupos para el laboratorio (lab.datahuba.com).

Los alumnos ponen su nombre; el docente pulsa «Armar grupos» y el servicio reparte
a todos en grupos de 2, de 3 y de 4 (mezclados distinto en cada tamaño).
Quien llega tarde entra solo al grupo más chico de cada tamaño.

Sin dependencias: solo la biblioteca estándar. Escucha en 127.0.0.1 y nginx le pasa /api/.
    LAB_CLAVE=...  LAB_DATOS=/var/lib/lab-grupos/salas.json  python3 lab_grupos.py 8766
Autoprueba del reparto:
    python3 lab_grupos.py --test
"""
import json
import math
import os
import random
import re
import sys
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CLAVE = os.environ.get("LAB_CLAVE", "")
DATOS = os.environ.get("LAB_DATOS", "salas.json")
TAMANOS = (2, 3, 4)
MAX_ALUMNOS = 200
LOCK = threading.Lock()


# ---------------------------------------------------------------- reparto
def tamanos_grupos(n, k):
    """Tamaños de los grupos para n personas con grupos «de k».
    Grupos parejos (difieren en 1 como mucho) y lo más cerca posible de k:
    7 de a 4 → [4, 3]; 3 de a 4 → [3]; 10 de a 3 → [4, 3, 3].
    Nunca deja un grupo demasiado chico: el mínimo es max(2, k−1) si hay gente para eso."""
    if n <= 0:
        return []
    g = max(1, math.floor(n / k + 0.5))
    minimo = max(2, k - 1)
    while g > 1 and n // g < minimo:
        g -= 1
    base, resto = divmod(n, g)
    return [base + 1] * resto + [base] * (g - resto)


def armar(ids, k, rng):
    orden = ids[:]
    rng.shuffle(orden)
    grupos, i = [], 0
    for t in tamanos_grupos(len(orden), k):
        grupos.append(orden[i:i + t])
        i += t
    return grupos


# ---------------------------------------------------------------- datos
def cargar():
    try:
        with open(DATOS, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def guardar(salas):
    tmp = DATOS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(salas, f, ensure_ascii=False)
    os.replace(tmp, DATOS)


def sala_nueva():
    return {"alumnos": [], "grupos": None, "armado": None}


def limpiar_nombre(s):
    s = re.sub(r"\s+", " ", str(s or "")).strip()
    return s[:40]


def limpiar_integ(g):
    """Señales de atención: salidas de la pestaña, texto pegado/copiado, extensiones, bloqueador."""
    if not isinstance(g, dict):
        return None
    n = lambda k: max(0, min(int(g.get(k) or 0), 10 ** 6))
    ext = g.get("ext") if isinstance(g.get("ext"), list) else []
    return {"salidas": n("salidas"), "fuera": n("fuera"), "pegados": n("pegados"), "copias": n("copias"),
            "ext": [re.sub(r"[^\w\-:.]", "", str(e))[:40] for e in ext[:8]], "adblock": bool(g.get("adblock"))}


def limpiar_avance(b):
    """Solo se guarda lo que el panel necesita, con tamaños acotados."""
    corto = lambda s, n: re.sub(r"[^\w.\-]", "", str(s))[:n]
    hechos = b.get("hechos") if isinstance(b.get("hechos"), list) else []
    intentos = b.get("intentos") if isinstance(b.get("intentos"), dict) else {}
    rep = b.get("repaso") if isinstance(b.get("repaso"), dict) else None
    return {
        "hechos": sorted({corto(h, 6) for h in hechos[:60]}),
        "intentos": {corto(k, 6): min(int(v), 99) for k, v in list(intentos.items())[:60]
                     if isinstance(v, (int, float))},
        "bloque": corto(b.get("bloque") or "", 10),
        "repaso": {"aciertos": int(rep.get("aciertos", 0)), "total": int(rep.get("total", 0))} if rep else None,
        "integ": limpiar_integ(b.get("integ")),
        "t": time.time(),
    }


def vista(sala):
    nombres = {a["id"]: a["nombre"] for a in sala["alumnos"]}
    grupos = None
    if sala["grupos"]:
        grupos = {k: [[{"id": i, "nombre": nombres.get(i, "?")} for i in g] for g in gs]
                  for k, gs in sala["grupos"].items()}
    return {"alumnos": [{"id": a["id"], "nombre": a["nombre"]} for a in sala["alumnos"]],
            "grupos": grupos, "armado": sala["armado"]}


# ---------------------------------------------------------------- HTTP
class H(BaseHTTPRequestHandler):
    server_version = "lab-grupos"

    def log_message(self, *a):
        pass

    def responder(self, code, obj):
        b = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def sala_id(self, valor):
        s = re.sub(r"[^a-z0-9-]", "", str(valor or "general").lower())[:30]
        return s or "general"

    def do_GET(self):
        if not self.path.startswith("/api/sala"):
            return self.responder(404, {"error": "no existe"})
        q = dict(p.split("=", 1) for p in self.path.partition("?")[2].split("&") if "=" in p)
        sid = self.sala_id(q.get("sala"))
        with LOCK:
            sala = cargar().get(sid) or sala_nueva()
        self.responder(200, vista(sala))

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length") or 0)
            if n > 4096:
                return self.responder(413, {"error": "demasiado grande"})
            body = json.loads(self.rfile.read(n) or b"{}")
        except (ValueError, TypeError):
            return self.responder(400, {"error": "json inválido"})
        sid = self.sala_id(body.get("sala"))
        ruta = self.path.split("?")[0]
        docente = ruta in ("/api/armar", "/api/reiniciar", "/api/quitar", "/api/panel")
        if docente and (not CLAVE or body.get("clave") != CLAVE):
            return self.responder(403, {"error": "clave incorrecta"})
        with LOCK:
            salas = cargar()
            if sid not in salas and len(salas) >= 50:
                return self.responder(409, {"error": "Demasiadas salas abiertas."})
            sala = salas.setdefault(sid, sala_nueva())
            if ruta == "/api/panel":                # docente: lista + avance de cada alumno
                return self.responder(200, {**vista(sala), "avance": {a["id"]: a.get("avance") for a in sala["alumnos"]},
                                            "ahora": time.time()})
            if ruta == "/api/avance":               # alumno: manda lo que lleva resuelto
                yo = next((a for a in sala["alumnos"] if a["id"] == str(body.get("id") or "")), None)
                if not yo:
                    return self.responder(404, {"error": "no registrado"})
                try:
                    yo["avance"] = limpiar_avance(body)
                except (ValueError, TypeError, OverflowError, AttributeError):
                    return self.responder(400, {"error": "avance inválido"})
                guardar(salas)
                return self.responder(200, {"ok": True})
            if ruta == "/api/registro":
                nombre = limpiar_nombre(body.get("nombre"))
                if len(nombre) < 2:
                    return self.responder(400, {"error": "Escribe tu nombre (al menos 2 letras)."})
                previo = str(body.get("id") or "")
                for a in sala["alumnos"]:
                    if a["id"] == previo:          # ya registrado: solo actualiza el nombre
                        a["nombre"] = nombre
                        guardar(salas)
                        return self.responder(200, {"id": previo, **vista(sala)})
                if len(sala["alumnos"]) >= MAX_ALUMNOS:
                    return self.responder(409, {"error": "La sala está llena."})
                nuevo = uuid.uuid4().hex[:12]
                sala["alumnos"].append({"id": nuevo, "nombre": nombre, "t": time.time()})
                if sala["grupos"]:                  # llegó tarde: al grupo más chico de cada tamaño
                    for gs in sala["grupos"].values():
                        min(gs, key=len).append(nuevo)
                guardar(salas)
                return self.responder(200, {"id": nuevo, **vista(sala)})
            if ruta == "/api/armar":
                ids = [a["id"] for a in sala["alumnos"]]
                if not ids:
                    return self.responder(400, {"error": "Todavía no hay nadie registrado."})
                rng = random.Random()
                sala["grupos"] = {str(k): armar(ids, k, rng) for k in TAMANOS}
                sala["armado"] = time.time()
            elif ruta == "/api/quitar":
                quitar = str(body.get("id") or "")
                sala["alumnos"] = [a for a in sala["alumnos"] if a["id"] != quitar]
                if sala["grupos"]:
                    for k, gs in sala["grupos"].items():
                        sala["grupos"][k] = [g for g in ([i for i in g if i != quitar] for g in gs) if g]
            elif ruta == "/api/reiniciar":
                salas[sid] = sala = sala_nueva()
            else:
                return self.responder(404, {"error": "no existe"})
            guardar(salas)
            return self.responder(200, vista(sala))


def _test():
    assert tamanos_grupos(7, 4) == [4, 3]
    assert tamanos_grupos(3, 4) == [3]
    assert tamanos_grupos(8, 4) == [4, 4]
    assert tamanos_grupos(5, 4) == [5]          # 3+2 dejaría un grupo de 2: mejor uno de 5
    assert tamanos_grupos(5, 2) == [3, 2]       # nadie queda solo en «pares»
    assert tamanos_grupos(1, 2) == [1]
    assert tamanos_grupos(10, 3) == [4, 3, 3]
    assert tamanos_grupos(30, 4) == [4] * 6 + [3] * 2
    for n in range(1, 120):
        for k in TAMANOS:
            t = tamanos_grupos(n, k)
            assert sum(t) == n and max(t) - min(t) <= 1, (n, k, t)
    av = limpiar_avance({"hechos": ["0.1", "<x>", "0.1"], "intentos": {"1.1": 3, "z": "no"},
                         "bloque": "b1", "repaso": {"aciertos": 5, "total": 12}})
    assert av["hechos"] == ["0.1", "x"] and av["intentos"] == {"1.1": 3} and av["repaso"]["total"] == 12
    g = armar(list("abcdefg"), 4, random.Random(1))
    assert sorted(sum(g, [])) == list("abcdefg") and [len(x) for x in g] == [4, 3]
    print("ok")


if __name__ == "__main__":
    if "--test" in sys.argv:
        _test()
    else:
        puerto = int(sys.argv[1]) if len(sys.argv) > 1 else 8766
        ThreadingHTTPServer(("127.0.0.1", puerto), H).serve_forever()
