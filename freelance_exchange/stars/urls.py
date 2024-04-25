from django.urls import path

from .views import *


urlpatterns = [
    path('list/', APIStar.as_view(), name='list_stars'),
    path('change/', StarChangeAPIView.as_view(), name='change_stars'),
    path('by_username/', GetByUsernameAPIStar.as_view(), name='find_stars_by_username'),
]
