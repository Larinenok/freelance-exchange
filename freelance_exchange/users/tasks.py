import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import TemporaryUserData

logger = logging.getLogger(__name__)

@shared_task
def delete_expired_temporary_users():
    logger.info("Запуск задачи по удалению устаревших пользователей...")
    now = timezone.now()
    expiration_time = now - timedelta(hours=5)
    logger.info(f"Текущее время: {now.isoformat()}")
    logger.info(f"Удалим всех, кто создан до: {expiration_time.isoformat()}")

    expired_users = TemporaryUserData.objects.filter(created_at__lt=expiration_time)
    count = expired_users.count()
    logger.info(f"Найдено {count} устаревших пользователей для удаления.")

    if count > 0:
        for user in expired_users:
            logger.info(f"Удаляется: {user.username} | created_at: {user.created_at.isoformat()}")

        try:
            expired_users.delete()
            logger.info(f"Удалено {count} пользователей.")
        except Exception as e:
            logger.error(f"Ошибка при удалении: {e}")
    else:
        logger.info("Нет пользователей для удаления.")
