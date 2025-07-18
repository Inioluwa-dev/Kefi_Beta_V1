"""
ASGI config for kefi_beta_version1 project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information, see:
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import dm.routing  # your app's websocket routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kefi_beta_version1.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            dm.routing.websocket_urlpatterns
        )
    ),
})




