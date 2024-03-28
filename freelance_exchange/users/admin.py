from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import *


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name']
    list_display_links = ['email', 'username']
    add_fieldsets = (
        *UserAdmin.add_fieldsets,
        (
            'Custom fields',
            {
                'fields': (
                    'email',
                    'first_name',
                    'last_name',
                )
            }
        )
    )
    fieldsets = (
        *UserAdmin.fieldsets,
        (
            'Custom fields',
            {
                'fields': (
                    'patronymic',
                    'slug',
                    'birth_date',
                    'phone',
                    'place_study_work',
                    'photo',
                    'description',
                    'skills',
                    'language',
                    'views',
                    'stars_freelancer',
                    'stars_customer'
                )
            }
        )
    )


class SkillsAdmin(admin.ModelAdmin):
    model = Skills
    list_display = ('name',)


admin.site.register(Skills, SkillsAdmin)
admin.site.register(Ip)
