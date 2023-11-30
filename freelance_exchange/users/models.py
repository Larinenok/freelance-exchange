from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
# from rest_framework.authtoken.models import Token

import json
import os.path


class Ip(models.Model):
    ip = models.CharField(max_length=100)

    def __str__(self):
        return self.ip

    class Meta:
        verbose_name = 'IP пользователя'
        verbose_name_plural = 'IP пользователей'


class CustomUser(AbstractUser):
    username = models.CharField(max_length=15, unique=True, verbose_name='Логин')
    slug = models.SlugField(max_length=15, unique=True, null=True, verbose_name='Slug')
    birth_date = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to="photos/%Y/%m/%d/", default='default/default.jpg', blank=True, verbose_name='Аватар')
    description = models.TextField(default='', blank=True, verbose_name='Описание')
    language = models.CharField(max_length=10, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE, verbose_name='Язык')
    views = models.ManyToManyField(Ip, blank=True, verbose_name='Просмотры профиля')
    stars_freelancer = models.JSONField(default=dict, blank=True, null=True)
    stars_customer = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']
