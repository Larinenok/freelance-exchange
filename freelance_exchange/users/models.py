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
        verbose_name = 'IP пользователей'
        verbose_name_plural = 'IP пользователей'


class Star(models.Model):
    count = models.IntegerField()

    def __str__(self):
        return str(self.count)

    class Meta:
        verbose_name = 'Звездочки пользователя'
        verbose_name_plural = 'Звездочки пользователя'


class CustomUser(AbstractUser):
    photo = models.ImageField(upload_to="photos/%Y/%m/%d/", default='default/default.jpg', blank=True, null=True)
    description = models.TextField(default='', blank=True)
    language = models.CharField(max_length=10, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE)
    views = models.ManyToManyField(Ip, blank=True)
    stars_freelancer = models.ForeignKey(Star, related_name='stars_freelancer', blank=True, on_delete=models.CASCADE, null=True)
    stars_customer = models.ForeignKey(Star, related_name='stars_customer', blank=True, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователи'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        print(Token.objects.create(user=instance))
