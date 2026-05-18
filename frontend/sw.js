const CACHE_NAME = "korean-app-v5";

const STATIC_ASSETS = [
  "/",
  "/index.html",
  "/css/style.css",
  "/css/ios-theme.css",
  "/manifest.json",
  "/icons/v4-book.svg",
  "/icons/icon-192.png",
  "/icons/icon-180.png",
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

// Immediately take over
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

// Clear ALL old caches and force reload all clients
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
    .then(() => self.clients.matchAll().then((clients) =>
      clients.forEach((client) => client.navigate(client.url))
    ))
  );
});

// Network first — always try to get fresh content
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);

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

  // Network first for everything — always fresh
  event.respondWith(
    fetch(event.request)
      .then((res) => {
        const clone = res.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        return res;
      })
      .catch(() => caches.match(event.request))
  );
});
