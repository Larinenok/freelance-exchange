from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import APIUser, DetailUserView, UserLoginAPIView, UserRegistrationAPIView, UserProfileView, SkillChangeView, \
    ActivateAccountView, PasswordResetRequestView, PasswordResetConfirmView, ChangePasswordView, BlacklistListView, \
    AddToBlacklistView, RemoveFromBlacklistView, UserListForUsers, PortfolioItemViewSet, CreateSkillsView

router = DefaultRouter()
router.register(r'portfolio', PortfolioItemViewSet, basename='portfolio')

urlpatterns = [
    path('list/', APIUser.as_view(), name='list_user'),
    path('login/', UserLoginAPIView.as_view()),
    path('register/', UserRegistrationAPIView.as_view(), name='register_user'),
    path('skills_create/', CreateSkillsView.as_view(), name='create_skills'),
    path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate_account'),
    path('password_reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password_reset_confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('skills_change/', SkillChangeView.as_view(), name='skills_change'),
    path('profile/', DetailUserView.as_view(), name='my_profile'),
    path('change_password/', ChangePasswordView.as_view(), name='change-password'),
    path('blacklist/', BlacklistListView.as_view(), name='blacklist-list'),
    path('blacklist/add/', AddToBlacklistView.as_view(), name='add-to-blacklist'),
    path('blacklist/remove/<int:blocked_user__id>/', RemoveFromBlacklistView.as_view(), name='remove-from-blacklist'),
    path('listfull/', UserListForUsers.as_view(), name='user-list-for-users'),
    path('', include(router.urls)),
    path('<slug:slug>/', UserProfileView.as_view(), name='user_profile'),
]
