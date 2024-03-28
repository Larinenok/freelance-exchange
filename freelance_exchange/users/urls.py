from django.urls import path

from .views import forget_password, signin, signup, get_users, get_access_token, get_me, telegram_login


urlpatterns = [
    # path('login/', MyObtainTokenPairView.as_view(), name='token_obtain_pair'),
    # path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', signin, name='login_token'),
    path('register/', signup, name='register_token'),
    path('refresh/', get_access_token, name='refresh_token'),
    path('', get_users, name='list_user'),
    path('me/', get_me, name='user'),
    path('forget/', forget_password, name='forget_password'),
    path('telegram_login/', telegram_login, name='telegram_login')
]
