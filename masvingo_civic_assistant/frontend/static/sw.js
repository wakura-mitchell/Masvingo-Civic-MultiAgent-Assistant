// Service Worker for Masvingo Civic Assistant PWA
const CACHE_NAME = "civic-assistant-v1.0.0";
const urlsToCache = [
	"/",
	"/static/manifest.json",
	"/static/css/main.css",
	"https://cdn.tailwindcss.com",
	"https://cdn.jsdelivr.net/npm/marked/marked.min.js",
	"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css",
];

// Install event - cache resources
self.addEventListener("install", (event) => {
	event.waitUntil(
		caches.open(CACHE_NAME).then((cache) => {
			console.log("Opened cache");
			return cache.addAll(urlsToCache);
		})
	);
});

// Fetch event - serve from cache when offline
self.addEventListener("fetch", (event) => {
	event.respondWith(
		caches.match(event.request).then((response) => {
			// Return cached version or fetch from network
			if (response) {
				return response;
			}
			return fetch(event.request);
		})
	);
});

// Activate event - clean up old caches
self.addEventListener("activate", (event) => {
	event.waitUntil(
		caches.keys().then((cacheNames) => {
			return Promise.all(
				cacheNames.map((cacheName) => {
					if (cacheName !== CACHE_NAME) {
						console.log("Deleting old cache:", cacheName);
						return caches.delete(cacheName);
					}
				})
			);
		})
	);
});

// Background sync for offline messages
self.addEventListener("sync", (event) => {
	if (event.tag === "background-sync") {
		event.waitUntil(doBackgroundSync());
	}
});

async function doBackgroundSync() {
	try {
		const cache = await caches.open("pending-requests");
		const requests = await cache.keys();

		for (const request of requests) {
			try {
				await fetch(request);
				await cache.delete(request);
			} catch (error) {
				console.log("Background sync failed for:", request.url);
			}
		}
	} catch (error) {
		console.log("Background sync error:", error);
	}
}
