# Generated by Django 3.2.13 on 2023-11-23 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0005_alter_adresponse_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adresponse',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
