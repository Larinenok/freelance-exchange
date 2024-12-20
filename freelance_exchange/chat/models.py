import os

from django.db import models
from django.conf import settings


class ChatRoom(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_rooms')
    created_chat_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания чата')

    class Meta:
        verbose_name_plural = 'Комнаты'
        verbose_name = 'Комната'

    def __str__(self):
        return f"Комната {self.id} с участниками: {', '.join([user.username for user in self.participants.all()])}"


def chat_file_upload_path(instance, filename):
    room_id = instance.room.id
    return os.path.join('chat_files', f'room_{room_id}', filename)


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField(verbose_name='Контент')
    file = models.FileField(upload_to=chat_file_upload_path, blank=True, null=True, verbose_name='Прикрепленный файл')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время отправки')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время обновления')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')

    class Meta:
        verbose_name_plural = 'Сообщения'
        verbose_name = 'Сообщение'
        ordering = ['created_at']

    def __str__(self):
        return f"Сообщение от {self.sender.username} в комнате {self.room.id}"

