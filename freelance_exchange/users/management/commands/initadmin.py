from django.conf import settings
from django.core.management.base import BaseCommand
from users.models import CustomUser


class Command(BaseCommand):
    def handle(self, *args, **options):
        username = 'admin'
        password = 'admin'
        print(f'Creating account for {username}')
        admin = CustomUser.objects.create_superuser(username=username, password=password)
        admin.is_active = True
        admin.is_admin = True
        admin.save()
