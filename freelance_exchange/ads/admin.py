from django.contrib import admin
from .models import *
from users.models import *


class AdFileAdmin(admin.StackedInline):
    model = AdFile


class AdResponseAdmin(admin.StackedInline):
    model = AdResponse


class AdAdmin(admin.ModelAdmin):
    model = Ad
    readonly_fields = ('id',)
    list_display = ('title', 'author', 'executor', 'status', 'deadlineStartAt', 'deadlineEndAt')
    search_fields = ('title', 'author__username', 'executor__username', 'orderNumber')
    list_filter = ('status', 'deadlineStartAt', 'deadlineEndAt', 'author')
    fieldsets = [
        ('Title/category', {'fields': ['title', 'category', 'slug', 'id']}),
        ('Content', {'fields': ['description', 'budget', 'status']}),
        ('Author', {'fields': ['author', 'contact_info']}),
        ('Executor', {'fields': ['executor']}),
    ]
    inlines = [AdFileAdmin]
    inlines = [AdResponseAdmin]
    prepopulated_fields = {'slug': ('title',)}

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


@admin.register(AdFile)
class AdFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'ad', 'file', 'scan')
    search_fields = ('ad__title', 'file')
    list_filter = ('ad',)


class AdResponseAdmin(admin.ModelAdmin):
    model = AdResponse
    list_display = ('ad', 'id', 'responder', 'response_comment')
    pass


class TypesAdmin(admin.ModelAdmin):
    model = Types
    list_display = ('name',)


class CategoriesAdmin(admin.ModelAdmin):
    model = Categories
    list_display = ('name',)


admin.site.register(Categories, CategoriesAdmin)
admin.site.register(Types, TypesAdmin)
admin.site.register(Ad, AdAdmin)
admin.site.register(AdResponse, AdResponseAdmin)
