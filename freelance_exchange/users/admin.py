from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from users.models import *


class CustomUserAdmin(admin.ModelAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('username', 'email')
    fieldsets = (('Main Fields',
        {'fields': (
            'first_name', 'last_name', 'username', 'slug', 'email', 'photo',
            'description', 'language', 'views', 'stars_freelancer', 'stars_customer',
            'phone_number', 'place_of_work', 'skills')}),)
    prepopulated_fields = {'slug': ('username',)}



admin.site.register(Ip)
admin.site.register(CustomUser, CustomUserAdmin)
