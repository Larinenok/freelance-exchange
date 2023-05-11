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
from rest_framework.authtoken import views
from rest_framework import permissions
# from rest_framework_swagger.views import get_swagger_view
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from freelance_exchange import settings
from users.views import home_view, profile, all_ads, ad_view, get_all_users_stars, get_user_stars, set_user_stars, delete_user_stars


schema_view = get_schema_view(
    openapi.Info(
        title="API",
        default_version='v1',
        description="asd",
        terms_of_service="asd",
        contact=openapi.Contact(email="asd@asd.com"),
        license=openapi.License(name="Awesome IP"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('', home_view),
    # path('api-token-auth/', views.obtain_auth_token),
    path('admin/', admin.site.urls),
    path('profile/<slug:slug_name>/', profile),
    path('auth/', include('users.urls')),
    path('ads/', all_ads),
    path('stars/', get_all_users_stars),
    path('stars/<slug:username>/', get_user_stars),
    path('stars/edit/<slug:username>/', set_user_stars),
    path('stars/delete/<slug:username>/', delete_user_stars),
    path('ads/<int:id>/<slug:slug_name>', ad_view)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
