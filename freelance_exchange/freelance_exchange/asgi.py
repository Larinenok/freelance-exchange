"""
ASGI config for freelance_exchange project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from channels.layers import get_channel_layer


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_exchange.settings')


django_asgi_app = get_asgi_application()

from channels_auth_token_middlewares.middleware import QueryStringSimpleJWTAuthTokenMiddleware
from chat.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_id>\d+)/$', ChatConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": django_asgi_app,

    "websocket": AllowedHostsOriginValidator(
        QueryStringSimpleJWTAuthTokenMiddleware(
            URLRouter(websocket_urlpatterns)
        )
    ),
})


