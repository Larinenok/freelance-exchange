import logging
import os

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import TemporaryUserData
from django.core.files.storage import default_storage

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


@shared_task
def delete_expired_temp_file():
    logger.info("Запуск задачи по удалению устаревших временных файлов...")

    base_temp_folder = 'temp_upload/'
    expiration_time = timezone.now() - timedelta(hours=5)

    if not default_storage.exists(base_temp_folder):
        logger.info(f"Папка {base_temp_folder} не найдена. Пропускаем.")
        return

    directories, files = default_storage.listdir(base_temp_folder)
    for dir_name in directories:
        dir_path = os.path.join(base_temp_folder, dir_name)
        subdirs, subfiles = default_storage.listdir(dir_path)
        for file_name in subfiles:
            file_path = os.path.join(dir_path, file_name)
            file_modified_time = default_storage.get_modified_time(file_path)

            if file_modified_time < expiration_time:
                logger.info(f"Удаляем устаревший файл: {file_path} (создан: {file_modified_time.isoformat()})")
                default_storage.delete(file_path)

    logger.info("Очистка временных файлов завершена.")
