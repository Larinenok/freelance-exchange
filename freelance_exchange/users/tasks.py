import logging
import os
import time

import requests
from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from decouple import config
from django.utils import timezone
from datetime import timedelta
from .models import TemporaryUserData
from django.core.files.storage import default_storage
from forum.models import UploadedFileScan

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

    try:
        files = default_storage.bucket.objects.filter(Prefix=base_temp_folder)
    except AttributeError:
        logger.error("Текущий storage не поддерживает прямой доступ к бакету. Нужно использовать S3Boto3Storage.")
        return

    deleted_files = 0

    for obj in files:
        file_path = obj.key
        file_modified_time = obj.last_modified

        if file_modified_time < expiration_time:
            logger.info(f"Удаляем файл: {file_path} (модифицирован: {file_modified_time.isoformat()})")
            default_storage.delete(file_path)
            deleted_files += 1

    logger.info(f"Очистка завершена. Удалено файлов: {deleted_files}.")


@shared_task
def start_file_scan_virustotal(scan_id, original_name, saved_path):
    logger.info(f"[SCAN #{scan_id}] Задача запущена для файла: {original_name} (путь: {saved_path})")

    scan = UploadedFileScan.objects.get(id=scan_id)
    api_key = config('API_KEY_VISUALTOTAL')
    try:
        file_size = default_storage.size(saved_path)
        headers = {
            "x-apikey": api_key,
            "accept": "application/json",
        }

        if file_size <= 32 * 1024 * 1024:
            logger.info(f"[SCAN #{scan_id}] Отправка файла напрямую (размер: {file_size} байт)")
            with default_storage.open(saved_path, 'rb') as f:
                files = {'file': (original_name, f)}
                response = requests.post("https://www.virustotal.com/api/v3/files", headers=headers, files=files)

        else:
            logger.info(f"[SCAN #{scan_id}] Файл превышает 32MB, получение upload_url")
            upload_url_resp = requests.get("https://www.virustotal.com/api/v3/files/upload_url", headers=headers)
            if upload_url_resp.status_code != 200:
                scan.status = "error"
                scan.save()
                return

            upload_url = upload_url_resp.json().get("data")
            if not upload_url:
                logger.error(f"[SCAN #{scan_id}] Пустой upload_url: {upload_url_resp.text}")
                scan.status = "error"
                scan.save()
                return

            with default_storage.open(saved_path, 'rb') as f:
                files = {'file': (original_name, f)}
                response = requests.post(upload_url, headers=headers, files=files)

            logger.info(f"[SCAN #{scan_id}] Файл загружен через upload_url, статус: {response.status_code}")

        if response.status_code != 200:
            logger.error(f"[SCAN #{scan_id}] Ошибка при отправке файла: {response.status_code} {response.text}")
            scan.status = "error"
            scan.save()
            return

        analysis_id = response.json().get("data", {}).get("id")
        if not analysis_id:
            logger.error(f"[SCAN #{scan_id}] analysis_id отсутствует! Ответ: {response.text}")
            scan.status = "error"
            scan.save()
            return

        scan.analysis_id = analysis_id
        scan.save()
        logger.info(f"[SCAN #{scan_id}] Файл отправлен на анализ, analysis_id: {analysis_id}")

        for attempt in range(15):
            time.sleep(5)
            analysis_result = requests.get(f"https://www.virustotal.com/api/v3/analyses/{analysis_id}", headers=headers)
            if analysis_result.status_code == 200:
                result_data = analysis_result.json()
                status_str = result_data["data"]["attributes"]["status"]
                logger.debug(f"[SCAN #{scan_id}] Попытка {attempt + 1}: статус анализа — {status_str}")
                if status_str == "completed":
                    stats = result_data["data"]["attributes"]["stats"]
                    malicious_count = stats.get("malicious", 0)
                    scan.status = "dangerous" if malicious_count > 0 else "safe"
                    scan.save()
                    logger.info(
                        f"[SCAN #{scan_id}] Анализ завершён. Статус: {scan.status}, malicious: {malicious_count}")

                    if scan.status == "dangerous":
                        try:
                            default_storage.delete(saved_path)
                            scan.was_deleted = True
                            scan.save()
                            logger.warning(f"[SCAN #{scan_id}] Опасный файл удалён из хранилища: {saved_path}")
                        except Exception as delete_err:
                            logger.exception(f"[SCAN #{scan_id}] Не удалось удалить опасный файл: {delete_err}")
                    break

        else:
            scan.status = "timeout"
            scan.save()
            logger.warning(f"[SCAN #{scan_id}] Истекло время ожидания завершения анализа")

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"scan_{scan_id}",
            {
                "type": "scan.status",
                "status": scan.status,
                "scan_id": scan_id,
                "was_deleted": scan.was_deleted
            }
        )
    except Exception as e:
        logger.exception(f"[SCAN #{scan_id}] Ошибка при анализе файла: {str(e)}")
        scan.status = "error"
        scan.save()
