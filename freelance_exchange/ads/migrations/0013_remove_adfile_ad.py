# Generated by Django 3.2.13 on 2024-09-19 03:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0012_adfile_ad'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='adfile',
            name='ad',
        ),
    ]
