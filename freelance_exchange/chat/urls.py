from django.urls import path
from .views import CreateMessageView

urlpatterns = [
    path('messages/', CreateMessageView.as_view(), name='create-message'),
]