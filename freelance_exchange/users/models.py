from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify

from stars.models import Star


class Ip(models.Model):
    ip = models.CharField(max_length=100)

    def __str__(self):
        return self.ip

    class Meta:
        verbose_name = 'IP пользователя'
        verbose_name_plural = 'IP пользователей'


class Skills(models.Model):
    name = models.CharField(max_length=50, verbose_name='Навыки')

    class Meta:
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    username = models.CharField(max_length=15, unique=True, verbose_name='Логин')
    first_name = models.CharField(max_length=150, blank=False, verbose_name='Имя')
    last_name = models.CharField(max_length=150, blank=False, verbose_name='Фамилия')
    email = models.EmailField(blank=True, verbose_name='Почта')
    patronymic = models.CharField(max_length=50, null=True, blank=True, verbose_name='Отчество')
    phone = models.CharField(max_length=30, null=True, blank=True, verbose_name='Телефон')
    place_study_work = models.CharField(max_length=100, null=True, blank=True, verbose_name='Место работы, учебы')
    slug = models.SlugField(max_length=15, unique=True, null=False, blank=False, verbose_name='Slug')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    skills = models.ManyToManyField(Skills, verbose_name='Навыки')
    photo = models.ImageField(upload_to="photos/%Y/%m/%d/", default='default/default.jpg', blank=True, verbose_name='Аватар')
    description = models.TextField(default='', blank=True, verbose_name='Описание')
    language = models.CharField(max_length=10, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE, verbose_name='Язык')
    views = models.ManyToManyField(Ip, blank=True, verbose_name='Просмотры профиля')
    stars = models.ManyToManyField(Star, blank=True, verbose_name='Рейтинг')
    # stars_freelancer = models.JSONField(default=dict, blank=True, null=True)
    # stars_customer = models.JSONField(default=dict, blank=True, null=True)

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
