from django.db import models


class Star(models.Model):
    author = models.CharField(max_length=15, verbose_name='Кто оставил отзыв')
    username = models.CharField(max_length=15, verbose_name='Кому отзыв')
    count = models.IntegerField(verbose_name='Оценка')

    def __str__(self):
        return str(self.author)

    class Meta:
        verbose_name = 'Рейтинг пользователя'
        verbose_name_plural = 'Рейтинг пользователя'
