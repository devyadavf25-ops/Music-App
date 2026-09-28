/**
 * Aura Music Platform — High Performance Offline Service Worker
 * Enables 100% offline standalone usage on iOS and Android Home Screens.
 */

const CACHE_NAME = "aura-music-v3.3";

const PRECACHE_ASSETS = [
  "./",
  "./index.html",
  "./styles.css",
  "./app.js",
  "./manifest.json",
  "./icon.svg",
  "./icon-192.png",
  "./icon-512.png",
  "./apple-touch-icon.png"
];

// Install: Cache all core assets for zero-network startup
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log("[Aura SW] Pre-caching offline app shell");
      return cache.addAll(PRECACHE_ASSETS);
    }).then(() => self.skipWaiting())
  );
});

// Activate: Clean up stale caches and take immediate control
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => {
          console.log("[Aura SW] Removing old cache:", key);
          return caches.delete(key);
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch: Network-First for app shell, cache fallback for offline
self.addEventListener("fetch", (event) => {
  const req = event.request;
  const url = new URL(req.url);

  // Bypass non-GET requests
  if (req.method !== "GET") return;

  // For API endpoints, try network first; if fail, return offline payload
  if (url.pathname.startsWith("/api/")) {
    event.respondWith(
      fetch(req).catch(() => {
        return new Response(
          JSON.stringify({
            offline: true,
            message: "Running in Offline Mode. Accessing local IndexedDB storage.",
            results: []
          }),
          {
            headers: { "Content-Type": "application/json" },
            status: 200
          }
        );
      })
    );
    return;
  }

  // For App Shell assets: Network First, falling back to Cache when offline
  event.respondWith(
    fetch(req)
      .then((networkResponse) => {
        if (
          networkResponse &&
          networkResponse.status === 200 &&
          (url.pathname.endsWith(".css") ||
           url.pathname.endsWith(".js") ||
           url.pathname.endsWith(".png") ||
           url.pathname.endsWith(".svg") ||
           url.pathname.endsWith(".html") ||
           url.pathname === "/")
        ) {
          const clone = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(req, clone));
        }
        return networkResponse;
      })
      .catch(() => {
        return caches.match(req).then((cachedResponse) => {
          if (cachedResponse) return cachedResponse;
          if (req.mode === "navigate") {
            return caches.match("./index.html");
          }
        });
      })
  );
});
