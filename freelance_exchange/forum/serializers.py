import uuid

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils.text import slugify
from rest_framework import serializers
from .models import Discussion, Comment, comment_file_upload_path, discussion_file_upload_path, UploadedFileScan
from users.models import CustomUser
from .utils import format_file_size


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name', 'photo', 'slug')
        ref_name = "ForumCustomUser"


class CommentSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    original_filename = serializers.SerializerMethodField()
    mime_type = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    formatted_file_size = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'content', 'author', 'created_at', 'file', 'original_filename', 'file_size', 'formatted_file_size', 'mime_type')

    def get_original_filename(self, obj):
        if obj.file:
            scan = UploadedFileScan.objects.filter(file_path__icontains=obj.file.name).first()
            return scan.original_filename if scan else None
        return None

    def get_mime_type(self, obj):
        if obj.file:
            scan = UploadedFileScan.objects.filter(file_path__icontains=obj.file.name).first()
            return scan.mime_type if scan else None
        return None

    def get_file_size(self, obj):
        if obj.file:
            try:
                return obj.file.size
            except Exception:
                return None
        return None

    def get_formatted_file_size(self, obj):
        return format_file_size(self.get_file_size(obj))


class DiscussionSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    resolved_comment = CommentSerializer(read_only=True)
    original_filename = serializers.SerializerMethodField()
    mime_type = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    formatted_file_size = serializers.SerializerMethodField()

    class Meta:
        model = Discussion
        fields = ('id', 'title', 'slug', 'description', 'file', 'original_filename', 'file_size', 'formatted_file_size', 'mime_type', 'created_at', 'status', 'author', 'comments', 'resolved_comment')

    def get_original_filename(self, obj):
        if obj.file:
            scan = UploadedFileScan.objects.filter(file_path__icontains=obj.file.name).first()
            return scan.original_filename if scan else None
        return None

    def get_mime_type(self, obj):
        if obj.file:
            scan = UploadedFileScan.objects.filter(file_path__icontains=obj.file.name).first()
            return scan.mime_type if scan else None
        return None

    def get_file_size(self, obj):
        if obj.file:
            try:
                return obj.file.size
            except Exception:
                return None
        return None

    def get_formatted_file_size(self, obj):
        return format_file_size(self.get_file_size(obj))


class DiscussionCreateSerializer(serializers.ModelSerializer):
    file = serializers.CharField(required=False, allow_blank=True)
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Discussion
        fields = ('id', 'title', 'description', 'file')

    def create(self, validated_data):
        user = self.context['request'].user
        title = validated_data.get('title')
        description = validated_data.get('description')
        file_path = validated_data.pop('file', None)

        discussion = Discussion.objects.create(
            author=user,
            title=title,
            description=description
        )
        discussion.save()

        if file_path:
            if default_storage.exists(file_path):
                with default_storage.open(file_path, 'rb') as old_file:
                    content = old_file.read()
                ext = file_path.split('.')[-1]
                filename = f"{uuid.uuid4()}.{ext}"

                discussion.file.save(filename, ContentFile(content))

                scan = UploadedFileScan.objects.filter(file_path=file_path).first()
                if scan:
                    scan.file_path = discussion.file.name
                    scan.save()

                default_storage.delete(file_path)

        return discussion


class CommentCreateSerializer(serializers.ModelSerializer):
    file = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Comment
        fields = ('content', 'file')

    def create(self, validated_data):
        user = self.context['request'].user
        discussion = self.context['discussion']

        file_path = validated_data.pop('file', None)

        comment = Comment.objects.create(
            author=user,
            discussion=discussion,
            content=validated_data.get('content', '')
        )

        if file_path:
            if default_storage.exists(file_path):
                with default_storage.open(file_path, 'rb') as old_file:
                    content = old_file.read()
                ext = file_path.split('.')[-1]
                filename = f"{uuid.uuid4()}.{ext}"

                comment.file.save(filename, ContentFile(content))

                scan = UploadedFileScan.objects.filter(file_path=file_path).first()
                if scan:
                    scan.file_path = comment.file.name
                    scan.save()

                default_storage.delete(file_path)

        return comment


class DiscussionUpdateStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discussion
        fields = ['status']

    def validate_status(self, value):
        if value not in ['resolved', 'open']:
            raise serializers.ValidationError("Статус должен быть 'resolved' или 'open'.")
        return value


class DiscussionMarkCommentSerializer(serializers.ModelSerializer):
    comment_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Discussion
        fields = ['comment_id']

    def validate_comment_id(self, value):
        try:
            comment = Comment.objects.get(id=value)
        except Comment.DoesNotExist:
            raise serializers.ValidationError("Комментарий с таким ID не найден.")
        return value

    def update(self, instance, validated_data):
        comment_id = validated_data.get('comment_id')
        comment = Comment.objects.get(id=comment_id)

        if comment.discussion != instance:
            raise serializers.ValidationError("Комментарий не принадлежит этому обсуждению.")

        instance.resolved_comment = comment
        instance.status = 'resolved'
        instance.save()
        return instance


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    type = serializers.type = serializers.ChoiceField(choices=['chat', 'discussion', 'comment', 'ad'], required=True)


class UploadedFileScanSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = UploadedFileScan
        fields = ['id', 'status', 'file_path', 'file_url', 'was_deleted']


    def get_file_url(self, obj):
        if obj.was_deleted:
            return None
        return default_storage.url(obj.file_path)


