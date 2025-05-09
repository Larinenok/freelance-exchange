from django.db import models
from django.conf import settings
import uuid
import os
from pytils.translit import slugify


def discussion_file_upload_path(instance, filename):
    print(f"DEBUG path — slug: {instance.slug}, id: {instance.id}")
    return f"forum/{instance.slug}/{filename}"


class Discussion(models.Model):
    STATUS_CHOICES = [
        ('open', 'Открыто'),
        ('resolved', 'Решено'),
    ]

    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    file = models.FileField(upload_to=discussion_file_upload_path, blank=True, null=True, verbose_name='Прикрепленный файл', max_length=511)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания обсуждения')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open', verbose_name='Статус')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='discussions', verbose_name='Автор обсуждения')
    resolved_comment = models.OneToOneField('Comment', on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_for', verbose_name='Решающий комментарий')
    slug = models.SlugField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Обсуждение'
        verbose_name_plural = 'Обсуждения'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"
        super(Discussion, self).save(*args, **kwargs)

    @property
    def resolved_comment_content(self):
        if self.resolved_comment:
            return self.resolved_comment.content
        return None

    def __str__(self):
        return self.title


def comment_file_upload_path(instance, filename):
    return f"forum/{instance.discussion.slug}/comment/{filename}"


class Comment(models.Model):
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='comments', verbose_name='Обсуждение')
    content = models.TextField(verbose_name='Контент комментария')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments', verbose_name='Автор комментария')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время комментария')
    file = models.FileField(upload_to=comment_file_upload_path, blank=True, null=True, verbose_name='Файл комментария', max_length=511)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']

    def __str__(self):
        return self.content


class UploadedFileScan(models.Model):
    file_path = models.CharField(max_length=500, verbose_name='Путь')
    original_filename = models.CharField(max_length=255, blank=True, null=True)
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    analysis_id = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Ожидание'),
        ('safe', 'Безопасный'),
        ('dangerous', 'Опасный'),
        ('error', 'Ошибка'),
    ], default='pending')
    was_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Загруженный файл'
        verbose_name_plural = 'Загруженные файлы'
        ordering = ['created_at']
