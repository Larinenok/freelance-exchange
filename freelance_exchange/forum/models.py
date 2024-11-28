from django.db import models
from django.conf import settings


class Discussion(models.Model):
    STATUS_CHOICES = [
        ('open', 'Открыто'),
        ('resolved', 'Решено'),
    ]

    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    file = models.FileField(upload_to='discussion_files/', blank=True, null=True, verbose_name='Прикрепленный файл')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания обсуждения')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open', verbose_name='Статус')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='discussions', verbose_name='Автор обсуждения')
    resolved_comment = models.OneToOneField('Comment', on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_for', verbose_name='Решающий комментарий')

    class Meta:
        verbose_name = 'Обсуждение'
        verbose_name_plural = 'Обсуждения'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Comment(models.Model):
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='comments', verbose_name='Обсуждение')
    content = models.TextField(verbose_name='Контент комментария')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments', verbose_name='Автор комментария')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время комментария')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']

    def __str__(self):
        return f"Комментарий от {self.author.username} к обсуждению '{self.discussion.title}'"

