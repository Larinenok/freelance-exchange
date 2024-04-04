from django.urls import path
from .views import APIUser, DetailUserView, UserLoginAPIView, UserRegistrationAPIView, UserProfileView, SkillChangeView

urlpatterns = [
    path('list/', APIUser.as_view(), name='list_user'),
    path('login/', UserLoginAPIView.as_view()),
    path('register/', UserRegistrationAPIView.as_view(), name='register_user'),
    path('skills_change/', SkillChangeView.as_view(), name='skills_change'),
    path('profile/', DetailUserView.as_view(), name='my_profile'),
    path('<slug:slug>/', UserProfileView.as_view(), name='user_profile'),
]
