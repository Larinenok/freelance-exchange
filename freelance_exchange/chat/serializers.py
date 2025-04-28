import uuid

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils.text import slugify
from rest_framework import serializers
from .models import ChatRoom, Message
from users.models import CustomUser
from ads.models import Ad


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'slug', 'first_name', 'last_name', 'photo')
        ref_name = "ChatCustomUser"


class MessageSerializer(serializers.ModelSerializer):
    sender = CustomUserSerializer()
    room = serializers.PrimaryKeyRelatedField(queryset=ChatRoom.objects.all())
    file = serializers.FileField(use_url=True)

    class Meta:
        model = Message
        fields = ('id', 'room', 'sender', 'content', 'file', 'created_at', 'updated_at', 'is_read')


class AdSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer

    class Meta:
        model = Ad
        fields = ('id', 'title', 'orderNumber', 'budget', 'author')


class ChatRoomSerializer(serializers.ModelSerializer):
    participants = CustomUserSerializer(many=True)
    messages = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    interlocutor = serializers.SerializerMethodField()
    is_closed = serializers.BooleanField()
    ad = AdSerializer()

    class Meta:
        model = ChatRoom
        fields = ['id', 'participants', 'interlocutor', 'created_at', 'last_message', 'messages', 'created_chat_at', 'is_closed', 'ad']

    def get_messages(self, obj):
        messages = obj.messages.all().order_by('created_at')
        return MessageSerializer(messages, many=True).data

    def get_last_message(self, obj):
        last_message = obj.messages.all().order_by('-created_at').first()
        if last_message:
            return MessageSerializer(last_message).data
        return None

    def get_created_at(self, obj):
        last_message = obj.messages.all().order_by('-created_at').first()
        if last_message:
            return last_message.created_at
        return None

    def get_interlocutor(self, obj):
        request_user = self.context['request'].user
        participants = obj.participants.exclude(id=request_user.id)
        if obj.participants.count() == 2 and participants.exists():
            return CustomUserSerializer(participants.first()).data
        return None


class MessageCreateSerializer(serializers.ModelSerializer):
    content = serializers.CharField()
    file = serializers.FileField(required=False, allow_null=True)

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

        content = validated_data.get('content', '')
        file = validated_data.pop('file', None)

        message = Message.objects.create(
            sender=sender,
            room=room,
            content=content
        )

        if file:
            old_path = file.name
            ext = old_path.split('.')[-1]
            ad_title = message.room.ad.title if message.room and message.room.ad else 'untitled'
            slug = slugify(ad_title)
            filename = f"{uuid.uuid4()}.{ext}"
            new_path = f"chat_files/{slug}/{filename}"

            if default_storage.exists(old_path):
                with default_storage.open(old_path, 'rb') as old_file:
                    default_storage.save(new_path, ContentFile(old_file.read()))
                default_storage.delete(old_path)

                message.file.name = new_path
                message.save()

        return message


class ChatCreateSerializer(serializers.ModelSerializer):
    participant_id = serializers.IntegerField(write_only=True)
    ad_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ChatRoom
        fields = ['participant_id', 'ad_id']

    def create(self, validated_data):
        user = self.context['request'].user
        participant_id = validated_data['participant_id']
        ad_id = validated_data['ad_id']

        try:
            participant = CustomUser.objects.get(id=participant_id)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден")

        try:
            ad = Ad.objects.get(id=ad_id)
        except Ad.DoesNotExist:
            raise serializers.ValidationError("Объявление не найдено")

        existing_chat = ChatRoom.objects.filter(
            ad=ad, participants=user
        ).filter(participants=participant).first()

        if existing_chat:
            return existing_chat

        chat_room = ChatRoom.objects.create(ad=ad)
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

