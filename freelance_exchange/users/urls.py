from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import signin, signup, get_users


urlpatterns = [
    # path('login/', MyObtainTokenPairView.as_view(), name='token_obtain_pair'),
    # path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', signin, name='login_token'),
    path('register/', signup, name='register_token'),
    path('refresh/', signin, name='refresh_token'),
    path('users/', get_users, name='users')
]
