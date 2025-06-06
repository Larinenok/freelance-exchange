from django.urls import path
from .views import MessageListCreateView, CreateChatView, ChatListView, ChatDetailView, AddParticipantsView, \
    CloseChatView, RequestAdminToChatView, AdminRequestedChatsView

urlpatterns = [
    path('<int:chat_id>/messages/', MessageListCreateView.as_view(), name='create-message'),
    path('create/', CreateChatView.as_view(), name='create-chat'),
    path('', ChatListView.as_view(), name='chat-list'),
    path('<int:id>/', ChatDetailView.as_view(), name='chat-detail'),
    path('<int:id>/add-participants/', AddParticipantsView.as_view(), name='add-participants'),
    path('<int:id>/close/', CloseChatView.as_view(), name='chat-close'),
    path('<int:id>/request-admin/', RequestAdminToChatView.as_view(), name='request-admin'),
    path('admin-requested-chats/', AdminRequestedChatsView.as_view(), name='admin-requested-chats'),
]