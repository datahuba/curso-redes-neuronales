/* Service worker del laboratorio: la página funciona sin internet una vez abierta.
   - La página (/) va por la red primero, para que siempre llegue la última versión; sin red, la copia guardada.
   - Fuentes e iconos: de la caché (no cambian).
   - /api/ (registro y grupos) nunca se guarda: siempre en vivo. */
const CACHE = "lab-v1";
const BASE = ["./", "manifest.json", "fuentes/outfit-latin.woff2", "fuentes/jetbrains-mono-latin.woff2",
  "iconos/icono-192.png", "iconos/icono-512.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(BASE)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener("fetch", e => {
  const req = e.request;
  const url = new URL(req.url);
  if (req.method !== "GET" || url.origin !== location.origin || url.pathname.startsWith("/api/")) return;

  if (req.mode === "navigate") {
    // la página: red primero (con lo nuevo), y si no hay red, la última guardada
    e.respondWith(fetch(req).then(r => {
      if (r.ok) { const copia = r.clone(); caches.open(CACHE).then(c => c.put("./", copia)); }
      return r;
    }).catch(() => caches.match("./")));
    return;
  }
  e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(r => {
    if (r.ok) { const copia = r.clone(); caches.open(CACHE).then(c => c.put(req, copia)); }
    return r;
  })));
});
