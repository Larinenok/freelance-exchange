from django.db import models
from users.models import CustomUser

class Discussion(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    # Статус обсуждения
    CLOSED = 'closed'
    IN_PROGRESS = 'in_progress'

    STATUS_CHOICES = [
        (CLOSED, 'Закрытое'),
        (IN_PROGRESS, 'Обсуждается'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=IN_PROGRESS, verbose_name='Статус')

class Comment(models.Model):
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE)
    commenter = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
