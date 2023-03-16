from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import *


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('username', 'email',)

CustomUserAdmin.fieldsets += (('Extra Fields', {'fields': (
                                       'photo', 'description', 'language', 'views', 'stars_freelancer', 'stars_customer',
                                   )}),)

admin.site.register(Ip)
admin.site.register(Star)
admin.site.register(CustomUser, CustomUserAdmin)
