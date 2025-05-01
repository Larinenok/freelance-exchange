from django.urls import path
from .views import APIStar, GetByUsernameAPIStar, StarChangeAPIView, StarRetrieveDestroyAPIView, UserStatsView


urlpatterns = [
    path('', APIStar.as_view(), name='all_stars'),
    path('get/<str:username>/', GetByUsernameAPIStar.as_view(), name='get-stars-by-username'),
    path('change/', StarChangeAPIView.as_view(), name='change-star'),
    path('<int:pk>/', StarRetrieveDestroyAPIView.as_view(), name='detail-star'),
    path('users-list-stats/', UserStatsView.as_view(), name='users-list-stats'),
]
