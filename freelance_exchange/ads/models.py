from django.db import models
from users.models import CustomUser
from pytils.translit import slugify
import os.path


class Ad(models.Model):
    author = models.ForeignKey(CustomUser, verbose_name='Заказчик', blank=True, null=True, on_delete=models.CASCADE, related_name='ads_author')
    executor = models.ForeignKey(CustomUser, verbose_name='Исполнитель', blank=True, null=True, on_delete=models.CASCADE, related_name='ads_executor')
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    orderNumber = models.IntegerField(verbose_name='Номер заказа', unique=True, blank=True)
    id = models.AutoField(primary_key=True)
    slug = models.SlugField(max_length=210, unique=False, null=True)
    description = models.TextField(max_length=1000, verbose_name='Описание')
    category = models.CharField(max_length=100, verbose_name='Категория')
    type = models.CharField(max_length=100, verbose_name='Вид', blank=True, null=True)
    budget = models.IntegerField(verbose_name='Бюджет')
    deadlineStartAt = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    deadlineEndAt = models.DateTimeField(verbose_name='Дата публикации', null=True)
    contact_info = models.CharField(max_length=200, verbose_name='Контактная информация')
    files = models.ManyToManyField('AdFile', related_name='ads', verbose_name='Файлы', blank=True)
    closed_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата закрытия')
    responders = models.ManyToManyField(CustomUser, through='AdResponse', related_name='ads_responded', verbose_name='Откликнувшиеся')

    # Статус объявления
    OPEN = 'open'
    CLOSED = 'closed'
    IN_PROGRESS = 'in_progress'

    STATUS_CHOICES = [
        (OPEN, 'Открытое'),
        (CLOSED, 'Закрытое'),
        (IN_PROGRESS, 'Выполняется'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=OPEN, verbose_name='Статус')

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Ad, self).save(*args, **kwargs)

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
    # ad = models.ForeignKey(Ad, on_delete=models.CASCADE, verbose_name='Объявление')
    file = models.FileField(upload_to='files', verbose_name='Файл')
    id = models.AutoField(primary_key=True)

    class Meta:
        verbose_name = 'Файлы из объявлений'
        verbose_name_plural = 'Файлы из объявлений'

    def __str__(self):
        return self.file.name
