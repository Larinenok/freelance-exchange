from django.contrib import admin
from .models import *
from users.models import *

class AdFileAdmin(admin.StackedInline):
    model = AdFile

class AdResponseAdmin(admin.StackedInline):
    model = AdResponse

class AdAdmin(admin.ModelAdmin):
    model = Ad
    fieldsets = [
        ("Title/category", {"fields": ["title", "category", "slug"]}),
        ("Content", {"fields": ["description", "budget"]}),
        ("Author", {"fields": ["author", "contact_info"]}),
        ("Executor", {"fields": ["executor"]}),
    ]
    inlines = [AdFileAdmin]
    inlines = [AdResponseAdmin]
    prepopulated_fields = {'slug': ('title',)}

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

class AdFileAdmin(admin.ModelAdmin):
    pass

class AdResponseAdmin(admin.ModelAdmin):
    model = AdResponse
    list_display = ('ad', 'id', 'responder', 'response_comment')
    pass

admin.site.register(Ad, AdAdmin)
admin.site.register(AdFile, AdFileAdmin)
admin.site.register(AdResponse, AdResponseAdmin)
