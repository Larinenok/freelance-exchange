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
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenRefreshView

from freelance_exchange import settings
from users.views import *
from ads.views import *
from stars.views import *


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
)

urlpatterns = [
    # path('signup/', signup, name='signup'),
    # path('signin/', signin, name='signin'),
    # path('refresh/', get_access_token, name='refresh'),
    # path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('testlogin/', )
    path('accounts/', include('django.contrib.auth.urls')),

    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('docs/terms_of_service/', terms_of_service),
    path('', home_view),
    # path('api-token-auth/', views.obtain_auth_token),
    path('admin/', admin.site.urls),
    path('profile/<slug:slug_name>/', profile),
    path('api/', include('users.urls')),
    path('me/', me),
    path('ads/', all_ads),
    path('ad/create/', create_ad),
    path('ad/edit/', edit_ad),
    path('ad/delete/', delete_ad),
    path('ad/upload/files/', AdFileUploadView.as_view(), name='file_upload'),
    path('stars/', get_all_users_stars),
    path('stars/<slug:username>/', get_user_stars),
    path('stars/edit/<slug:username>/', set_user_stars),
    path('stars/delete/<slug:username>/', delete_user_stars),
    path('ads/<int:id>-<str:slug>/', ad_view),
    path('api/ads/', api_ad_view),
    path('ad/response/', response_ad),
    # path('api/ad_responders/', get_responders),
    path('api/ad_responses/', get_responses),
    path('ad/set_executor/', set_executor),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
