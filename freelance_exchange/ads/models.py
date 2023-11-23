from django.db import models
from users.models import CustomUser
import os.path


class Ad(models.Model):
    author = models.ForeignKey(CustomUser, verbose_name='Заказчик', blank=True, null=True, on_delete=models.CASCADE, related_name='ads_author')
    executor = models.ForeignKey(CustomUser, verbose_name='Исполнитель', blank=True, null=True, on_delete=models.CASCADE, related_name='ads_executor')
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    id = models.AutoField(primary_key=True)
    slug = models.SlugField(max_length=210, unique=False, null=True)
    description = models.TextField(max_length=1000, verbose_name='Описание')
    category = models.CharField(max_length=100, verbose_name='Категория')
    budget = models.IntegerField(verbose_name='Бюджет')
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    contact_info = models.CharField(max_length=200, verbose_name='Контактная информация')
    # В КОДЕ НЕ ИСПОЛЬЗУЕТСЯ ¯\_(ツ)_/¯ НО МАЛО ЛИ
    responders = models.ManyToManyField(CustomUser, through='AdResponse', related_name='ads_responded', verbose_name='Откликнувшиеся')

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'

    def __str__(self):
        return self.title

class AdResponse(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, verbose_name='Объявление')
    responder = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Откликнувшийся')
    response_comment = models.TextField(max_length=1000, verbose_name='Комментарий отклика')
    id = models.AutoField(primary_key=True)

    class Meta:
        verbose_name = 'Отклик'
        verbose_name_plural = 'Отклики'

    def __str__(self):
        return self.responder.username

class AdFile(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, verbose_name='Объявление')
    file = models.FileField(upload_to='files', verbose_name='Файл')

    class Meta:
        verbose_name = 'Файлы из объявлений'
        verbose_name_plural = 'Файлы из объявлений'

    def __str__(self):
        return os.path.basename(self.file.name)
