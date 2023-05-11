import os.path

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from rest_framework.authtoken.models import Token

class Ip(models.Model):
    ip = models.CharField(max_length=100)

    def __str__(self):
        return self.ip

    class Meta:
        verbose_name = 'IP пользователя'
        verbose_name_plural = 'IP пользователей'


class Star(models.Model):
    count = models.IntegerField()

    def __str__(self):
        return str(self.count)

    class Meta:
        verbose_name = 'Звездочки пользователя'
        verbose_name_plural = 'Звездочки пользователя'


class CustomUser(AbstractUser):
    username = models.CharField(max_length=15, unique=True, verbose_name='Логин')
    slug = models.SlugField(max_length=15, unique=True, null=True, verbose_name='Slug')
    photo = models.ImageField(upload_to="photos/%Y/%m/%d/", default='default/default.jpg', blank=True, verbose_name='Аватар')
    description = models.TextField(default='', blank=True, verbose_name='Описание')
    language = models.CharField(max_length=10, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE, verbose_name='Язык')
    views = models.ManyToManyField(Ip, blank=True, verbose_name='Просмотры профиля')
    stars_freelancer = models.ForeignKey(Star, related_name='stars_freelancer', blank=True, on_delete=models.CASCADE, null=True, verbose_name='Оценка исполнителя')
    stars_customer = models.ForeignKey(Star, related_name='stars_customer', blank=True, on_delete=models.CASCADE, null=True, verbose_name='Оценка заказчика')

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username', 'password']
class Ad(models.Model):
    author = models.ForeignKey(CustomUser, verbose_name='Автор поста', blank=True, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    id = models.AutoField(primary_key=True)
    slug = models.SlugField(max_length=210, unique=False, null=True)
    description = models.TextField(max_length=1000, verbose_name='Описание')
    category = models.CharField(max_length=100, verbose_name='Категория')
    budget = models.IntegerField(verbose_name='Бюджет')
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    contact_info = models.CharField(max_length=200, verbose_name='Контактная информация')

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'

    def __str__(self):
        return self.title

class AdFile(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, verbose_name='Объявление')
    file = models.FileField(upload_to='files', verbose_name='Файл')

    class Meta:
        verbose_name = 'Файлы из объявлений'
        verbose_name_plural = 'Файлы из объявлений'

    def __str__(self):
        return os.path.basename(self.file.name)



@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        print(Token.objects.create(user=instance))
