const CACHE_NAME = "korean-app-v3";

const STATIC_ASSETS = [
  "/",
  "/index.html",
  "/css/style.css",
  "/css/ios-theme.css",
  "/manifest.json",
  "/js/app.js",
  "/js/services/api-client.js",
  "/js/services/local-cache.js",
  "/js/services/tts.js",
  "/js/i18n.js",
  "/js/components/search-page.js",
  "/js/components/word-detail.js",
  "/js/components/conjugation-table.js",
  "/js/components/sentence-page.js",
  "/js/components/favorites-page.js",
  "/js/components/settings-page.js",
  "/js/utils/pwa-register.js",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);

  // NetworkFirst for API calls
  if (url.pathname.startsWith("/api/")) {
    event.respondWith(
      fetch(event.request)
        .then((res) => {
          const clone = res.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          return res;
        })
        .catch(() => caches.match(event.request))
    );
    return;
  }

  // CacheFirst for static assets
  event.respondWith(
    caches.match(event.request).then((cached) => cached || fetch(event.request))
  );
});
