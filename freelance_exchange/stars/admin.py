from django.contrib import admin
from .models import Star


@admin.register(Star)
class StarAdmin(admin.ModelAdmin):
    list_display = ('author', 'target', 'ad', 'count', 'created_at')
    search_fields = ('author__username', 'target__username', 'message', 'ad__title')
    list_filter = ('count', 'created_at', 'ad')
    raw_id_fields = ('ad',)
