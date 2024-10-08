# Generated by Django 3.2.13 on 2024-03-14 03:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0009_alter_adfile_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='ad',
            name='closed_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата закрытия'),
        ),
        migrations.AddField(
            model_name='ad',
            name='status',
            field=models.CharField(choices=[('open', 'Открытое'), ('closed', 'Закрытое'), ('in_progress', 'Выполняется')], default='open', max_length=20, verbose_name='Статус'),
        ),
    ]
