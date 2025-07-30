self.addEventListener('install', (e) => {
  console.log('Service Worker installed');
});

self.addEventListener('fetch', function(event) {
  // Možeš dodati offline cache ovde
});
