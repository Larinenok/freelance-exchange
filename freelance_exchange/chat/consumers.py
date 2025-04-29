import uuid

from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

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
def save_message(room, sender, content, file_path=None):
    message = Message.objects.create(room=room, sender=sender, content=content)

    if file_path and default_storage.exists(file_path):
        with default_storage.open(file_path, 'rb') as temp_file:
            file_data = temp_file.read()

        ext = file_path.split('.')[-1]
        filename = f"{uuid.uuid4()}.{ext}"

        message.file.save(filename, ContentFile(file_data))
        default_storage.delete(file_path)

    return message


@database_sync_to_async
def get_file_url(message):
    return message.file.url if message.file else None


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


@database_sync_to_async
def mark_unread_messages_as_read(user, room):
    messages = Message.objects.filter(room=room, is_read=False).exclude(sender=user)
    messages.update(is_read=True)


@database_sync_to_async
def get_sender_data(user):
    return {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'slug': user.slug,
        'photo': user.photo.url if user.photo else None,
    }


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

        await mark_unread_messages_as_read(self.scope['user'], self.room)

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
            room_id = self.scope['url_route']['kwargs']['room_id']

            room = await get_chat_room(room_id)
            if not room:
                await self.close()
                return

            if isinstance(message_data.get("message"), str):
                content = message_data["message"]
                file_path = None
            else:
                content = message_data["message"].get("content", "")
                file_path = message_data["message"].get("file")

            message = await save_message(room, sender, content, file_path)

            sender_data = await get_sender_data(sender)
            file_url = await get_file_url(message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat.message',
                    'message': content,
                    'sender': sender_data,
                    'timestamp': message.created_at.isoformat(),
                    'messageId': message.id,
                    'file': file_url,
                    'is_read': False,
                    'room_id': room_id
                }
            )

            recipient_user = await database_sync_to_async(
                lambda: room.participants.exclude(id=sender.id).first()
            )()
            if recipient_user:
                await self.channel_layer.group_send(
                    f"user_{recipient_user.id}",
                    {
                        "type": "new_message_notification",
                        "room_id": room.id,
                        "chat_id": room.id,
                        "message": message.content,
                        "timestamp": message.created_at.isoformat(),
                        "messageId": message.id,
                        "sender_id": sender_data['id'],
                        "sender_username": sender_data['username'],
                        "sender_slug": sender_data['slug'],
                        "sender_first_name": sender_data.get('first_name'),
                        "sender_last_name": sender_data.get('last_name'),
                        "sender_photo": sender_data.get('photo'),
                    }
                )

        except Exception as e:
            logger.error(f"WebSocket  receive error: {e}")
            await self.close()

    async def chat_message(self, event):
        try:
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

            await self.send(text_data=json.dumps({
                'message': message,
                'sender': sender,
                'timestamp': timestamp,
                'messageId': message_id,
                'file': file_url,
                'room_id': room_id,
                'is_read': is_read,
            }))

        except Exception as e:
            logger.warning(f"Failed to send chat message to WebSocket: {e}")


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

        try:
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

        except Exception as e:
            logger.warning(f"Failed to send notification to WebSocket: {e}")


class FileScanConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.scan_id = self.scope['url_route']['kwargs']['scan_id']
        self.group_name = f'scan_{self.scan_id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def scan_status(self, event):
        await self.send(text_data=json.dumps({
            "status": event["status"],
            "scan_id": event["scan_id"],
            "was_deleted": event.get("was_deleted", False)
        }))
