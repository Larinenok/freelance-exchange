from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

User = get_user_model()


class CustomJWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        return CustomJWTAuthMiddlewareInstance(scope, self)


class CustomJWTAuthMiddlewareInstance:
    def __init__(self, scope, middleware):
        self.scope = dict(scope)
        self.middleware = middleware

    async def __call__(self, receive, send):
        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        self.scope['user'] = await self.get_user(token)
        inner = self.middleware.inner(self.scope)
        return await inner(receive, send)

    @database_sync_to_async
    def get_user(self, token):
        try:
            access_token = AccessToken(token)
            user = User.objects.get(id=access_token['user_id'])
            return user
        except Exception as e:
            print("JWT auth failed:", e)
            return AnonymousUser()
