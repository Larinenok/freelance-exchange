from django.contrib import admin
from .models import Discussion, Comment


@admin.register(Discussion)
class AdminDiscussion(admin.ModelAdmin):
    list_display = ('title', 'description', 'author', 'status', 'created_at', 'resolved_comment_content')
    list_display_links = ('title', 'description')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description', 'author__username')

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'file', 'author', 'status')
        }),
        ('Решающий комментарий', {
            'fields': ('resolved_comment',),
        }),
        ('Временные метки', {
            'fields': ('created_at',),
        }),
    )

    readonly_fields = ('created_at', 'resolved_comment_content')

    def resolved_comment_content(self, obj):
        return obj.resolved_comment.content if obj.resolved_comment else "Не указан"
    resolved_comment_content.short_description = 'Решающий комментарий'


@admin.register(Comment)
class AdminComment(admin.ModelAdmin):
    list_display = ('discussion', 'author', 'created_at', 'content')
    list_filter = ('discussion', 'created_at')
    search_fields = ('content', 'author__username', 'discussion__title')

    fieldsets = (
        ('Информация о комментарии', {
            'fields': ('discussion', 'content', 'author')
        }),
        ('Временные метки', {
            'fields': ('created_at',),
        }),
    )

    readonly_fields = ('created_at',)
