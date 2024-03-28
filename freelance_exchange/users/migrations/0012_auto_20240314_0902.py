# Generated by Django 3.2.13 on 2024-03-14 02:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_delete_star'),
    ]

    operations = [
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Навык',
                'verbose_name_plural': 'Навык',
            },
        ),
        migrations.AddField(
            model_name='customuser',
            name='phone_number',
            field=models.CharField(blank=True, max_length=12, null=True, unique=True, verbose_name='Номер телефона'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='place_of_work',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Место работы/учебы'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='skills',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.skill', verbose_name='Навыки'),
        ),
    ]