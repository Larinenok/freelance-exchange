# Generated by Django 3.2.13 on 2024-04-11 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stars', '0006_auto_20240411_1248'),
        ('users', '0016_auto_20240411_1214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='stars',
            field=models.ManyToManyField(blank=True, to='stars.Star', verbose_name='Рейтинг'),
        ),
    ]