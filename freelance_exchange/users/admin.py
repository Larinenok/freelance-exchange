from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import *


class CustomUserAdmin(admin.ModelAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('username', 'email')
    fieldsets = (('Main Fields',
                  {'fields': (
                            'first_name', 'last_name', 'username', 'slug', 'email', 'photo',
                            'description', 'language', 'views', 'stars_freelancer', 'stars_customer',)}),)
    prepopulated_fields = {'slug': ('username',)}

class AdFileAdmin(admin.StackedInline):
    model = AdFile

class AdAdmin(admin.ModelAdmin):
    model = Ad
    fieldsets = [
        ("Title/category", {"fields": ["title", "category", "slug"]}),
        ("Content", {"fields": ["description", "budget"]}),
        ("Author", {"fields": ["author", "contact_info"]})
    ]
    inlines = [AdFileAdmin]
    prepopulated_fields = {'slug': ('title',)}

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

class AdFileAdmin(admin.ModelAdmin):
    pass


admin.site.register(Ip)
admin.site.register(Star)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Ad, AdAdmin)
admin.site.register(AdFile, AdFileAdmin)
