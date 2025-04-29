from django.contrib import admin
from .models import Discussion, Comment, UploadedFileScan


@admin.register(Discussion)
class AdminDiscussion(admin.ModelAdmin):
    list_display = ('title',  'slug', 'description', 'author', 'status', 'created_at', 'resolved_comment_content')
    list_display_links = ('title', 'description')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description', 'author__username')

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'description', 'file', 'author', 'status')
        }),
        ('Решающий комментарий', {
            'fields': ('resolved_comment',),
        }),
        ('Временные метки', {
            'fields': ('created_at',),
        }),
    )
    prepopulated_fields = {'slug': ('title',)}

    readonly_fields = ('created_at', 'resolved_comment_content')

    def resolved_comment_content(self, obj):
        return obj.resolved_comment.content if obj.resolved_comment else "Не указан"
    resolved_comment_content.short_description = 'Решающий комментарий'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


@admin.register(Comment)
class AdminComment(admin.ModelAdmin):
    list_display = ('discussion', 'author', 'created_at', 'content', 'file')
    list_filter = ('discussion', 'created_at')
    search_fields = ('content', 'author__username', 'discussion__title')

    fieldsets = (
        ('Информация о комментарии', {
            'fields': ('discussion', 'content', 'author', 'file')
        }),
        ('Временные метки', {
            'fields': ('created_at',),
        }),
    )

    readonly_fields = ('created_at',)

@admin.register(UploadedFileScan)
class UploadedFileScanAdmin(admin.ModelAdmin):
    list_display = ('id', 'file_path', 'status', 'was_deleted', 'created_at')
    list_filter = ('status', 'was_deleted', 'created_at')
    search_fields = ('file_path', 'analysis_id')
    ordering = ('-created_at',)