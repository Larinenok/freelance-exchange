from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    def handle(self, *args, **options):
        User = get_user_model()
        username = 'admin'
        password = 'admin'

        if User.objects.filter(username=username).exists():
            print(f'Пользователь с именем {username} уже существует. Пропуск создания.')
        else:
            print(f'Создание учётной записи для {username}')
            admin = User.objects.create_superuser(username=username, password=password)
            admin.is_active = True
            admin.is_admin = True
            admin.save()
            print(f'Учётная запись для {username} успешно создана.')
