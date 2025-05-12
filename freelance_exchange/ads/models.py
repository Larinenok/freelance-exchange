import uuid

from django.db import models
from users.models import CustomUser
from pytils.translit import slugify
import os.path
from forum.models import UploadedFileScan
from django.core.validators import MinValueValidator, MaxValueValidator


class Types(models.Model):
    name = models.CharField(max_length=255, verbose_name='Типы работ')

    class Meta:
        verbose_name = 'Вид'
        verbose_name_plural = 'Виды'

    def __str__(self):
        return self.name


class Categories(models.Model):
    name = models.CharField(max_length=255, verbose_name='Категории')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Ad(models.Model):
    author = models.ForeignKey(CustomUser, verbose_name='Заказчик', blank=True, null=True, on_delete=models.CASCADE, related_name='ads_author')
    executor = models.ForeignKey(CustomUser, verbose_name='Исполнитель', blank=True, null=True, on_delete=models.CASCADE, related_name='ads_executor')
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    orderNumber = models.IntegerField(verbose_name='Номер заказа', unique=True, blank=True)
    id = models.AutoField(primary_key=True)
    slug = models.SlugField(max_length=210, unique=False, null=True)
    description = models.TextField(verbose_name='Описание')
    budget = models.IntegerField(
        verbose_name='Бюджет',
        validators=[
            MinValueValidator(1, message="Бюджет должен быть положительным"),
            MaxValueValidator(100_000_000, message="Слишком большой бюджет — ограничение 100 млн")
        ]
    )
    deadlineStartAt = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    deadlineEndAt = models.DateTimeField(verbose_name='Дедлайн', null=True)
    contact_info = models.CharField(max_length=200, verbose_name='Контактная информация')
    closed_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата закрытия')
    responders = models.ManyToManyField(CustomUser, through='AdResponse', related_name='ads_responded', verbose_name='Откликнувшиеся')
    type = models.ManyToManyField(Types, verbose_name='Виды')
    category = models.ManyToManyField(Categories, verbose_name='Категории')

    # Статус объявления
    OPEN = 'open'
    CLOSED = 'closed'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'

    STATUS_CHOICES = [
        (OPEN, 'Открыто'),
        (IN_PROGRESS, 'Выполняется'),
        (COMPLETED, 'Выполнено'),
        (CLOSED, 'Закрыто'),
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


def ad_file_upload_path(instance, filename):
    slug = instance.ad.slug or slugify(instance.ad.title)
    unique_id = uuid.uuid4().hex[:8]
    return f"ad/{slug}-{unique_id}/{filename}"


class AdFile(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='files', verbose_name='Объявление')
    file = models.FileField(upload_to=ad_file_upload_path, verbose_name='Файл', max_length=511)
    scan = models.OneToOneField(UploadedFileScan, on_delete=models.SET_NULL, null=True, blank=True)

    def delete(self, *args, **kwargs):
        if self.file:
            self.file.delete(save=False)
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'Файлы из объявлений'
        verbose_name_plural = 'Файлы из объявлений'

    def __str__(self):
        return self.file.name
