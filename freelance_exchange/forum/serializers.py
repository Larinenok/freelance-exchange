from rest_framework import serializers
from .models import Discussion, Comment
from users.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name', 'photo')
        ref_name = "ForumCustomUser"


class CommentSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'content', 'author', 'created_at')


class DiscussionSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    resolved_comment = CommentSerializer(read_only=True)

    class Meta:
        model = Discussion
        fields = ('id', 'title', 'description', 'file', 'created_at', 'status', 'author', 'comments', 'resolved_comment')


class DiscussionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discussion
        fields = ('title', 'description', 'file', 'status')


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('content', )


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


