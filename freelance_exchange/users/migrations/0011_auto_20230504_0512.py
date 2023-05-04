# Generated by Django 3.2.13 on 2023-05-04 02:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_alter_customuser_stars_freelancer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='stars_customer',
        ),
        migrations.AddField(
            model_name='customuser',
            name='stars_customer',
            field=models.JSONField(default=dict, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='stars_freelancer',
            field=models.JSONField(default=dict, null=True),
        ),
    ]
