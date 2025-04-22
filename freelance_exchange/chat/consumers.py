from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import ChatRoom, Message
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@database_sync_to_async
def get_chat_room(room_id):
    try:
        return ChatRoom.objects.get(id=room_id)
    except ChatRoom.DoesNotExist:
        return None


@database_sync_to_async
def get_user_by_id(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None


@database_sync_to_async
def save_message(room, sender, content):
    return Message.objects.create(room=room, sender=sender, content=content)


@database_sync_to_async
def mark_message_as_read(message_id):
    try:
        message = Message.objects.get(id=message_id)
        if not message.is_read:
            message.is_read = True
            message.save()
        return message.is_read
    except Message.DoesNotExist:
        return False


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        logger.info(f"Authenticated user in scope: {self.scope['user']}")

        if self.scope['user'].is_anonymous:
            await self.close()
            return

        self.room = await get_chat_room(self.room_id)
        if not self.room:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            message_data = json.loads(text_data)
            sender = self.scope['user']
            message_content = message_data.get('message')
            room_id = self.scope['url_route']['kwargs']['room_id']

            room = await get_chat_room(room_id)

            message = await save_message(room, sender, message_content)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat.message',
                    'message': message_content,
                    'sender': {
                        'id': sender.id,
                        'username': sender.username,
                        'first_name': sender.first_name,
                        'last_name': sender.last_name,
                        'slug': sender.slug,
                        'photo': sender.photo.url if sender.photo else None,
                    },
                    'timestamp': message.created_at.isoformat(),
                    'messageId': message.id,
                    'file': message.file.url if message.file else None,
                    'is_read': False,
                    'room_id': room_id
                }
            )

            recipient_user = room.participants.exclude(id=sender.id).first()
            if recipient_user:
                await self.channel_layer.group_send(
                    f"user_{recipient_user.id}",
                    {
                        "type": "new_message_notification",
                        "room_id": room.id,
                        "message": message.content,
                        "timestamp": message.created_at.isoformat(),
                        "messageId": message.id,
                        "sender_id": sender.id,
                        "sender_username": sender.username,
                        "sender_slug": sender.slug,
                        "sender_first_name": sender.first_name,
                        "sender_last_name": sender.last_name,
                        "sender_photo": sender.photo.url if sender.photo else None,
                    }
                )

        except Exception as e:
            logger.error(f"WebSocket  receive error: {e}")
            await self.close()

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        timestamp = event['timestamp']
        message_id = event['messageId']
        file_url = event['file']
        room_id = event.get('room_id')

        current_user = self.scope['user']
        is_read = False
        if current_user.id != sender['id']:
            is_read = await mark_message_as_read(message_id)

        sender_data = {
            'id': sender.get('id'),
            'username': sender.get('username'),
            'slug': sender.get('slug'),
            'photo': sender.get('photo'),
        }

        if sender.get('first_name'):
            sender_data['first_name'] = sender['first_name']
        if sender.get('last_name'):
            sender_data['last_name'] = sender['last_name']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender_data,
            'timestamp': timestamp,
            'messageId': message_id,
            'file': file_url,
            'room_id': room_id,
            'is_read': is_read,
        }))


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
            return

        self.user_group_name = f"user_{self.user.id}"

        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"User {self.user.username} connected to notification channel.")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

    async def new_message_notification(self, event):

        sender = {
            'id': event.get('sender_id'),
            'username': event.get('sender_username'),
            'slug': event.get('sender_slug'),
            'photo': event.get('sender_photo'),
        }

        if event.get('sender_first_name'):
            sender['first_name'] = event['sender_first_name']
        if event.get('sender_last_name'):
            sender['last_name'] = event['sender_last_name']

        await self.send(text_data=json.dumps({
            "type": "notification",
            "chat_id": event["chat_id"],
            "room_id": event.get("room_id"),
            "messageId": event.get("messageId"),
            "message_preview": event["message"],
            "sender": sender,
            "timestamp": event["timestamp"],
            "is_read": False
        }))
