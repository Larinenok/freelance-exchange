# Generated by Django 3.2.13 on 2024-05-02 03:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stars', '0006_auto_20240411_1248'),
    ]

    operations = [
        migrations.AddField(
            model_name='star',
            name='message',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Отзыв'),
        ),
    ]
