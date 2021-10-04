"""
ASGI config for commerce project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import auctions
import os
from channels.routing import ProtocolTypeRouter,URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import auctions.routing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'commerce.settings')

application = ProtocolTypeRouter({
    "http":get_asgi_application(),
    "websocket":AuthMiddlewareStack(URLRouter(auctions.routing.websocket_urlpatterns))
})
