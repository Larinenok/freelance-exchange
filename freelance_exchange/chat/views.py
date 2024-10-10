from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView, ListCreateAPIView
from .serializers import MessageCreateSerializer, MessageSerializer, ChatCreateSerializer, ChatRoomSerializer, \
    AddParticipantsSerializer
from .models import ChatRoom, Message


class MessageListCreateView(ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        chat_id = self.kwargs.get('chat_id')
        user = self.request.user

        return Message.objects.filter(room__id=chat_id)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MessageCreateSerializer
        return MessageSerializer

    def list(self, request, *args, **kwargs):
        chat_id = self.kwargs.get('chat_id')
        user = self.request.user

        Message.objects.filter(room__id=chat_id, is_read=False).exclude(sender=user).update(is_read=True)

        queryset = self.get_queryset()
        serializer = MessageSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        chat_id = self.kwargs.get('chat_id')
        data = request.data.copy()
        data['room_id'] = chat_id

        serializer = self.get_serializer(data=data, context={'request': request, 'chat_id': chat_id})
        serializer.is_valid(raise_exception=True)
        message = serializer.save()

        return Response({
            'content': message.content,
            'file': message.file.url if message.file else None
        }, status=status.HTTP_201_CREATED)


class CreateChatView(CreateAPIView):
    serializer_class = ChatCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        chat_room = serializer.save()

        return Response({
            "chat": chat_room.id,
            "participants": [user.username for user in chat_room.participants.all()]
        }, status=status.HTTP_201_CREATED)


class ChatListView(ListAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(participants=user)


class ChatDetailView(RetrieveAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]
    queryset = ChatRoom.objects.all()
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(participants=user)


class AddParticipantsView(UpdateAPIView):
    serializer_class = AddParticipantsSerializer
    permission_classes = [IsAdminUser]
    queryset = ChatRoom.objects.all()
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        chat_room = self.get_object()
        serializer = self.get_serializer(chat_room, data=request.data)
        serializer.is_valid(raise_exception=True)
        chat_room = serializer.save()

        return Response({
            "chat_id": chat_room.id,
            "participants": [user.username for user in chat_room.participants.all()]
        }, status=status.HTTP_200_OK)


