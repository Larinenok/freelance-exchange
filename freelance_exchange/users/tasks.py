import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import TemporaryUserData

logger = logging.getLogger(__name__)


@shared_task
def delete_expired_temporary_users():
    logger.info("Запуск задачи по удалению устаревших пользователей...")
    expiration_time = timezone.now() - timedelta(hours=24)
    expired_users = TemporaryUserData.objects.filter(created_at__lt=expiration_time)
    count = expired_users.count()
    logger.info(f"Найдено {count} устаревших пользователей для удаления.")
    expired_users.delete()
    logger.info(f"Удалено {count} устаревших пользователей.")
