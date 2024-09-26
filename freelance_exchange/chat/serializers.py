from rest_framework import serializers
from .models import ChatRoom, Message
from users.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name')


class MessageSerializer(serializers.ModelSerializer):
    sender = CustomUserSerializer()
    room = serializers.PrimaryKeyRelatedField(queryset=ChatRoom.objects.all())
    file = serializers.FileField(use_url=True)

    class Meta:
        models = CustomUser
        fields = ('id', 'room', 'sender', 'content', 'file', 'created_at', 'updated_at', 'is_read')


class ChatRoomSerializer(serializers.ModelSerializer):
    participants = CustomUserSerializer(many=True)
    messages = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'participants', 'created_at', 'messages', 'last_message']

    def get_messages(self, obj):
        messages = obj.messages.all().order_by('created_at')
        return MessageSerializer(messages, many=True).data

    def get_last_message(self, obj):
        last_message = obj.messages.all().order_by('-created_at').first()
        if last_message:
            return MessageSerializer(last_message).data
        return None


class MessageCreateSerializer(serializers.ModelSerializer):
    sender_id = serializers.IntegerField(write_only=True)
    room_id = serializers.IntegerField(write_only=True)
    content = serializers.CharField()
    file = serializers.FileField(required=False)

    class Meta:
        model = Message
        fields = ['sender_id', 'room_id', 'content', 'file']

    def create(self, validated_data):
        sender_id = validated_data.pop('sender_id')
        room_id = validated_data.pop('room_id')

        sender = CustomUser.objects.get(id=sender_id)
        room = ChatRoom.objects.get(id=room_id)

        message = Message.objects.create(
            sender=sender,
            room=room,
            **validated_data
        )
        return message
