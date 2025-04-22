from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@database_sync_to_async
def get_user(token):
    try:
        access_token = AccessToken(token)
        return User.objects.get(id=access_token['user_id'])
    except Exception as e:
        print("JWT auth failed:", e)
        logger.error(f"JWT auth failed: {e}")
        return AnonymousUser()


class CustomJWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_string = scope['query_string'].decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        user = await get_user(token)
        scope['user'] = user

        logger.info(f"[JWT Middleware] User: {user}")

        return await self.inner(scope, receive, send)
