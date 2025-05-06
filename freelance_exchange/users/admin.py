from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import *


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name']
    list_display_links = ['email', 'username']
    readonly_fields = ['stars']
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
                    'is_approved',
                    'stars'
                )
            }
        )
    )


class SkillsAdmin(admin.ModelAdmin):
    model = Skills
    list_display = ('name',)


class TemporaryUserDataAdmin(admin.ModelAdmin):
    model = TemporaryUserData
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'created_at'
    )


class BlakListAdmin(admin.ModelAdmin):
    model = BlackList
    list_display = (
        'owner',
        'blocked_user'
    )


class PortfoliAdmin(admin.ModelAdmin):
    model = PortfolioItem
    list_display = (
        'user',
        'title',
        'file',
        'uploaded_at'
    )


admin.site.register(Skills, SkillsAdmin)
admin.site.register(Ip)
admin.site.register(TemporaryUserData, TemporaryUserDataAdmin)
admin.site.register(BlackList, BlakListAdmin)
admin.site.register(PortfolioItem, PortfoliAdmin)
