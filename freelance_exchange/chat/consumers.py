from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import ChatRoom, Message

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


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

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
        message_data = json.loads(text_data)
        sender_id = message_data.get('senderId')
        message_content = message_data.get('message')
        room_id = self.scope['url_route']['kwargs']['room_id']

        room = await database_sync_to_async(get_chat_room)(room_id)
        sender = await database_sync_to_async(get_user_by_id)(sender_id)

        message = Message(room=room, sender=sender, content=message_content)
        await database_sync_to_async(message.save)()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat.message',
                'message': message_content,
                'senderId': sender_id,
                'timestamp': message.created_at.isoformat(),
                'messageId': message.id,
                'file': message.file.url if message.file else None,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender_id = event['senderId']
        timestamp = event['timestamp']
        message_id = event['messageId']
        file_url = event['file']

        sender = await database_sync_to_async(get_user_by_id)(sender_id)

        if sender:
            sender_data = {
                'id': sender.id,
                'username': sender.username,
            }

            if sender.last_name:
                sender_data['last_name'] = sender.last_name
            if sender.first_name:
                sender_data['first_name'] = sender.first_name

            await self.send(text_data=json.dumps({
                'message': message,
                'sender': sender_data,
                'timestamp': timestamp,
                'messageId': message_id,
                'file': file_url,
            }))
        else:
            await self.send(text_data=json.dumps({
                'message': message,
                'senderId': sender_id,
                'timestamp': timestamp,
                'messageId': message_id,
                'file': file_url,
            }))

