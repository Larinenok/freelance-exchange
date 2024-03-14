from django.urls import path

from .views import *


urlpatterns = [
    path('', all_ads),
    path('create/', create_ad),
    path('edit/', edit_ad),
    path('delete/', delete_ad),
    path('get/', api_ad_view),
    path('get_responses/', get_responses),
    path('set_executor/', set_executor),
    path('adsview/<int:id>/', ad_view),
    path('send_response/', response_ad),
    path('ad_list/', get_ads),
    path('upload_files/', add_file_to_ad),
    path('file_list/', list_files_for_ad),
    path('file_delete/', delete_file_from_ad),
    path('close/', close_ad),
]
