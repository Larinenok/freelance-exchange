from django.urls import path
from .views import (
    AdListCreateView,
    AdDetailView,
    AdFileUploadView,
    AdFileListView,
    AdFileDeleteView,
    AdResponseView,
    AdExecutorView,
    UserAdsView,
    UserClosedAdsView,
    AdsInProgressView,
    CloseAdView,
    # DeleteAdView,
    GetResponsesView
)

urlpatterns = [
    path('ads/', AdListCreateView.as_view(), name='ad-list'),
    path('ads/<int:pk>/', AdDetailView.as_view(), name='ad-detail'),
    path('ads/files/upload/', AdFileUploadView.as_view(), name='ad-file-upload'),
    path('ads/files/', AdFileListView.as_view(), name='ad-file-list'),
    path('ads/files/delete/', AdFileDeleteView.as_view(), name='ad-file-delete'),
    path('ads/response/', AdResponseView.as_view(), name='ad-response'),
    path('ads/executor/', AdExecutorView.as_view(), name='ad-executor'),
    path('users/ads/', UserAdsView.as_view(), name='user-ads'),
    path('users/ads/closed/', UserClosedAdsView.as_view(), name='user-closed-ads'),
    path('users/ads/in-progress/', AdsInProgressView.as_view(), name='ads-in-progress'),
    path('ads/close/', CloseAdView.as_view(), name='close-ad'),
    # path('ads/delete/', DeleteAdView.as_view(), name='delete-ad'),
    path('ads/responses/', GetResponsesView.as_view(), name='get-responses'),
]
