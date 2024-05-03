# from background_task import background
# from django.utils import timezone
# from datetime import timedelta
# from .models import TemporaryUserData


# @background(schedule=3600)
# def delete_expired_temp_users():
#     expiration_date = timezone.now() - timedelta(days=1)
#     TemporaryUserData.objects.filter(created_at__lte=expiration_date).delete()
