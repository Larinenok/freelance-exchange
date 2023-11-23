# Generated by Django 3.2.13 on 2023-11-02 02:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ad',
            fields=[
                ('title', models.CharField(max_length=200, verbose_name='Заголовок')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('slug', models.SlugField(max_length=210, null=True)),
                ('description', models.TextField(max_length=1000, verbose_name='Описание')),
                ('category', models.CharField(max_length=100, verbose_name='Категория')),
                ('budget', models.IntegerField(verbose_name='Бюджет')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
                ('contact_info', models.CharField(max_length=200, verbose_name='Контактная информация')),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ads_author', to=settings.AUTH_USER_MODEL, verbose_name='Автор поста')),
            ],
            options={
                'verbose_name': 'Объявление',
                'verbose_name_plural': 'Объявления',
            },
        ),
        migrations.CreateModel(
            name='AdFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='files', verbose_name='Файл')),
                ('ad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ads.ad', verbose_name='Объявление')),
            ],
            options={
                'verbose_name': 'Файлы из объявлений',
                'verbose_name_plural': 'Файлы из объявлений',
            },
        ),
    ]