# Generated by Django 3.2.13 on 2023-04-27 03:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20230427_0648'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='stars_freelancer',
            field=models.JSONField(default="{'username': None, 'star': 0}", null=True),
        ),
    ]