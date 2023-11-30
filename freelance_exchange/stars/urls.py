from django.urls import path

from .views import *


urlpatterns = [
    path('', get_all_users_stars),
    path('<slug:username>/', get_user_stars),
    path('edit/<slug:username>/', set_user_stars),
    path('delete/<slug:username>/', delete_user_stars),
]
