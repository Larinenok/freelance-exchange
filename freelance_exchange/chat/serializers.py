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
        model = Message
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
    content = serializers.CharField()
    file = serializers.FileField(required=False)

    class Meta:
        model = Message
        fields = ('content', 'file')

    def create(self, validated_data):
        sender = self.context['request'].user
        room_id = self.context['chat_id']

        try:
            room = ChatRoom.objects.get(id=room_id)
        except ChatRoom.DoesNotExist:
            raise serializers.ValidationError("Комната чата не найдена.")

        message = Message.objects.create(
            sender=sender,
            room=room,
            **validated_data
        )
        return message


class ChatCreateSerializer(serializers.ModelSerializer):
    participant_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ChatRoom
        fields = ['participant_id']

    def create(self, validated_data):
        user = self.context['request'].user
        participant_id = validated_data['participant_id']

        try:
            participant = CustomUser.objects.get(id=participant_id)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден")

        chat_room = ChatRoom.objects.filter(participants=user).filter(participants=participant).first()
        if chat_room:
            return chat_room

        chat_room = ChatRoom.objects.create()
        chat_room.participants.add(user, participant)
        return chat_room


class AddParticipantsSerializer(serializers.ModelSerializer):
    participant_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )

    class Meta:
        model = ChatRoom
        fields = ['participant_ids']

    def update(self, instance, validated_data):
        participant_ids = validated_data['participant_ids']

        participants = CustomUser.objects.filter(id__in=participant_ids)
        if participants.count() != len(participant_ids):
            raise serializers.ValidationError("Один или несколько пользователей не найдены.")

        instance.participants.add(*participants)
        return instance

