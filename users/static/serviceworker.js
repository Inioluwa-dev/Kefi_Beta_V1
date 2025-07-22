self.addEventListener('push', function(event) {
    var data = event.data.json();
    event.waitUntil(
        self.registration.showNotification(data.title || data.head || 'Notification', {
            body: data.body,
            icon: data.icon || '/static/core/img/logo.png'
        })
    );
});
