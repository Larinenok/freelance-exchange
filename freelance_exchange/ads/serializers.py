from django.conf import settings
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from pytils.translit import slugify
from .models import Ad, AdFile, AdResponse
from users.models import CustomUser

class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name', 'photo', 'slug', 'patronymic')

class AdCreateSerializer(serializers.ModelSerializer):
    # files = serializers.PrimaryKeyRelatedField(queryset=AdFile.objects.all(), many=True, required=False)
    # author = UserResponseSerializer(read_only=True)
    # responders = UserResponseSerializer(many=True, read_only=True)
    # deadlineStartAt = serializers.DateTimeField(read_only=True)
    # status = serializers.CharField(read_only=True)
    class Meta:
        model = Ad
        fields = (
            'id', 'orderNumber', 'title',
            'type', 'category', 'deadlineEndAt', 'budget', 'description',
        )

    def create(self, validated_data):
        files = validated_data.pop('files', [])
        # Извлекаем текущего пользователя из контекста
        author = self.context['request'].user
        ad = Ad.objects.create(**validated_data, slug=slugify(validated_data['title']))
        for file in files:
            ad.files.add(file)
        return ad

    def update(self, instance, validated_data):
        files = validated_data.pop('files', [])
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.category = validated_data.get('category', instance.category)
        instance.type = validated_data.get('type', instance.type)
        instance.budget = validated_data.get('budget', instance.budget)
        instance.contact_info = validated_data.get('contact_info', instance.contact_info)
        instance.save()

        # Update files
        if files:
            instance.files.clear()
            for file in files:
                instance.files.add(file)

        return instance

class AdGetSerializer(serializers.ModelSerializer):
    author = UserResponseSerializer(read_only=True)
    responders = UserResponseSerializer(many=True, read_only=True)
    files = serializers.PrimaryKeyRelatedField(queryset=AdFile.objects.all(), many=True, required=False)

    class Meta:
        model = Ad
        fields = (
            'id', 'orderNumber', 'responders', 'title',
            'type', 'category', 'status', 'deadlineStartAt',
            'deadlineEndAt', 'budget', 'description',
            'author', 'files',
        )

class AdFileUploadSerializer(serializers.ModelSerializer):
    files = serializers.ListField(child=serializers.FileField(), required=True)

    class Meta:
        model = AdFile
        fields = ('id', 'files')

    def create(self, validated_data):
        ad_files = []
        for file in validated_data['files']:
            ad_file = AdFile(file=file)
            ad_file.save()
            ad_files.append(ad_file)
        return ad_files

    def update(self, instance, validated_data):
        for i, file in enumerate(validated_data.get('files', [])):
            if i < len(instance):
                instance[i].file = file
                instance[i].save()
            else:
                ad_file = AdFile(file=file)
                ad_file.save()
                instance.append(ad_file)
        return instance


class AdResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdResponse
        fields = ('id', 'ad', 'responder', 'response_comment')


class AdFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdFile
        fields = ('id', 'file')
