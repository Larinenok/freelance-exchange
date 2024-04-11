from django.urls import path

from .views import *


urlpatterns = [
    path('list/', APIStar.as_view(), name='list_stars'),
    path('change/', StarChangeAPIView.as_view(), name='change_stars'),
]
