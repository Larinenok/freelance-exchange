"""freelance_exchange URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from drf_yasg.generators import OpenAPISchemaGenerator
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from freelance_exchange import settings
from users.views import *
from ads.views import *
from stars.views import *


class CustomSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = ['https', 'http']  # Добавьте необходимые схемы
        return schema


schema_view = get_schema_view(
    openapi.Info(
        title="API",
        default_version='v1',
        description="API for freelance exchanges",
        terms_of_service="terms_of_service/",
        contact=openapi.Contact(email="asd@asd.com"),
        license=openapi.License(name="Здесь может быть ваша реклама"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    generator_class=CustomSchemaGenerator,
)

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),

    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('admin/', admin.site.urls),
    # --- USERS ---
    path('api/users/', include('users.urls')),
    # --- ADS ---
    path('api/ad/', include('ads.urls')),
    # --- STARS ---
    path('api/stars/', include('stars.urls')),

    path('api/chats/', include('chat.urls')),

    path('api/discussions/', include('forum.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
