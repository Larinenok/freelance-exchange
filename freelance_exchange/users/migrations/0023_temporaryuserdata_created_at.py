# Generated by Django 3.2.13 on 2024-04-25 04:53

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_auto_20240425_1142'),
    ]

    operations = [
        migrations.AddField(
            model_name='temporaryuserdata',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
