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

from freelance_exchange import settings
from users.views import home_view, profile, all_ads

urlpatterns = [
    path('', home_view),
    # path('api-token-auth/', views.obtain_auth_token),
    path('admin/', admin.site.urls),
    path('profile/<slug:slug_name>/', profile),
    path('auth/', include('users.urls')),
    path('ads/', all_ads),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
