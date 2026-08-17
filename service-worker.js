// Deutsch Karten — service worker
// Estrategia:
//  - App shell (HTML/CSS/JS/íconos/vendor): cache-first, se actualiza en segundo plano.
//  - data/vocab-a1.json: network-first con fallback a cache (para poder actualizar
//    contenido en el futuro sin romper el uso offline).
//
// IMPORTANTE: subí CACHE_NAME cada vez que cambies cualquier archivo cacheado,
// si no los usuarios van a seguir viendo la versión vieja hasta que iOS decida
// revisar el service worker.

const CACHE_NAME = 'deutsch-karten-v2';

// Nota: las librerías de import de Anki (jszip, sql.js) NO están acá a
// propósito — son pesadas (~700KB) y solo hacen falta si el usuario usa esa
// función, así que se cargan perezosamente (ver js/anki-import.js) en vez de
// engordar la instalación inicial de la PWA.
const APP_SHELL = [
  './',
  './index.html',
  './manifest.json',
  './css/styles.css',
  './js/app.js',
  './js/fsrs.js',
  './js/storage.js',
  './js/tts.js',
  './js/levels.js',
  './js/quiz.js',
  './js/vendor/ts-fsrs.mjs',
  './data/vocab-a1.json',
  './data/vocab-a2.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-512-maskable.png',
  './icons/apple-touch-icon.png',
];

// Cubre data/vocab-a1.json, vocab-a2.json, y los niveles que se agreguen a futuro.
const DATA_URL_PATTERN = /\/data\/vocab-[a-z0-9]+\.json$/;

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(APP_SHELL))
      .catch((err) => {
        // No dejamos que un solo asset faltante rompa la instalación entera.
        console.warn('[sw] precache falló parcialmente', err);
      })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((names) =>
      Promise.all(
        names
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      )
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return; // no interceptamos CDNs externos

  if (DATA_URL_PATTERN.test(url.pathname)) {
    event.respondWith(networkFirst(request));
  } else {
    event.respondWith(cacheFirst(request));
  }
});

async function cacheFirst(request) {
  const cached = await caches.match(request);
  const network = fetch(request)
    .then((response) => {
      if (response && response.ok) {
        caches.open(CACHE_NAME).then((cache) => cache.put(request, response.clone()));
      }
      return response;
    })
    .catch(() => null);

  // stale-while-revalidate: devolvemos cache ya si existe, actualizamos en bg
  if (cached) {
    network; // dispara la actualización, no esperamos
    return cached;
  }
  const fresh = await network;
  return fresh || cached || Response.error();
}

async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response && response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch (err) {
    const cached = await caches.match(request);
    if (cached) return cached;
    throw err;
  }
}

// Permite que app.js le pida al SW que chequee actualizaciones al volver a foco
// (iOS no revisa el service worker en background).
self.addEventListener('message', (event) => {
  if (event.data === 'skipWaiting') {
    self.skipWaiting();
  }
});
