import re
import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from pytils.translit import slugify
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError


def user_photo_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f"{instance.username}/photo/{filename}"


def user_portfolio_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}'.{ext}"
    return f"{instance.user.username}/portfolio/{filename}"


class Ip(models.Model):
    ip = models.CharField(max_length=100)

    def __str__(self):
        return self.ip

    class Meta:
        verbose_name = 'IP пользователя'
        verbose_name_plural = 'IP пользователей'


class Skills(models.Model):
    name = models.CharField(max_length=255, verbose_name='Навыки')

    class Meta:
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'

    def __str__(self):
        return self.name


class TemporaryUserData(models.Model):
    username = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Временное хранилище пользователей'
        verbose_name_plural = 'Хранилище'

    def __str__(self):
        return self.username


class CustomUser(AbstractUser):
    username = models.CharField(max_length=15, unique=True, verbose_name='Логин')
    first_name = models.CharField(max_length=150, blank=False, verbose_name='Имя')
    last_name = models.CharField(max_length=150, blank=False, verbose_name='Фамилия')
    email = models.EmailField(unique=True, blank=True, verbose_name='Почта')
    patronymic = models.CharField(max_length=50, null=True, blank=True, verbose_name='Отчество')
    phone = models.CharField(max_length=30, null=True, blank=True, verbose_name='Телефон')
    place_study_work = models.CharField(max_length=100, null=True, blank=True, verbose_name='Место работы, учебы')
    slug = models.SlugField(max_length=15, unique=True, null=False, blank=False, verbose_name='Slug')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    skills = models.ManyToManyField(Skills, verbose_name='Навыки')
    photo = models.ImageField(upload_to=user_photo_path, default='default/default.jpg', blank=True, verbose_name='Аватар')
    description = models.TextField(default='', blank=True, verbose_name='Описание')
    language = models.CharField(max_length=10, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE, verbose_name='Язык')
    views = models.ManyToManyField(Ip, blank=True, verbose_name='Просмотры профиля')
    stars = models.FloatField(null=True, blank=True, verbose_name='Рейтинг')
    is_approved = models.BooleanField(default=False, verbose_name='Подтвержден')

    def clean(self):
        super().clean()
        if not re.match(r'^[a-zA-Z0-9_]+$', self.username):
            raise ValidationError({'username': "Логин может содержать только латинские буквы, цифры и подчеркивания."})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.username)
        super(CustomUser, self).save(*args, **kwargs)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']


class PasswordResetToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    email_sent = models.BooleanField(default=True)

    def mark_as_used(self):
        self.is_used = True
        self.save()

    def can_send_new_request(user):
        latest_request = PasswordResetToken.objects.filter(user=user).order_by('-created_at').first()
        if not latest_request:
            return True, None
        if not latest_request.is_used:
            return False, "Письмо уже отправлено на почту."
        cooldown_period = timezone.timedelta(days=90)
        time_since_last_used = timezone.now() - latest_request.created_at
        if time_since_last_used > cooldown_period:
            return True, None
        remaining_time = cooldown_period - time_since_last_used
        remaining_minutes = int(remaining_time.total_seconds() // (3600*24))
        return False, f"Следующую возможность сброса пароля можно будет использовать через {remaining_minutes} дней."


class BlackList(models.Model):
    owner = models.ForeignKey(CustomUser, related_name='blacklist_owner', on_delete=models.CASCADE)
    blocked_user = models.ForeignKey(CustomUser, related_name='blocked_user', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Черный список'
        verbose_name_plural = 'Черный список'
        unique_together = ('owner', 'blocked_user')

    def __str__(self):
        return f"{self.owner.username} заблокировал {self.blocked_user.username}"


class PortfolioItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='portfolio_items')
    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    file = models.FileField(upload_to=user_portfolio_path, verbose_name='Файл')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Файл работы'
        verbose_name_plural = 'Файлы работ'
