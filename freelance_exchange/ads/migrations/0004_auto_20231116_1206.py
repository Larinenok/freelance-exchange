# Generated by Django 3.2.13 on 2023-11-16 05:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0003_auto_20231102_1139'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='adresponse',
            options={'verbose_name': 'Отклик', 'verbose_name_plural': 'Отклики'},
        ),
        migrations.AlterField(
            model_name='adresponse',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
