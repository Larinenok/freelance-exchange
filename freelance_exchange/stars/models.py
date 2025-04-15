from django.db import models
from users.models import CustomUser


class Star(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='given_ratings', verbose_name='Кто оставил отзыв')
    target = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_ratings', verbose_name='Кому отзыв')
    ad = models.ForeignKey('ads.Ad', on_delete=models.CASCADE, related_name='stars', verbose_name='Объявление', null=True, blank=True)
    count = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name='Оценка')
    message = models.CharField(max_length=200, null=True, blank=True, verbose_name='Отзыв')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Рейтинг пользователя'
        verbose_name_plural = 'Рейтинг пользователя'
        unique_together = ('author', 'target', 'ad')

    def __str__(self):
        return f'{self.author} → {self.target} за {self.ad.title} ({self.count}★)'

