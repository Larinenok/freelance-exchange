from django.urls import path

from .views import *


urlpatterns = [
    path('', all_ads),
    path('create/', create_ad),
    path('edit/', edit_ad),
    path('delete/', delete_ad),
    path('upload/files/', AdFileUploadView.as_view(), name='file_upload'),
    path('get/', api_ad_view),
    path('get_responses/', get_responses),
    path('set_executor/', set_executor),
    path('adsview/<int:id>/', ad_view),
    path('send_response/', response_ad),
    path('list/', get_ads),
]
