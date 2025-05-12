import os.path
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from pytils.translit import slugify
from .models import Ad, AdFile, AdResponse, Types, Categories
from users.models import CustomUser
from forum.models import UploadedFileScan
from forum.utils import format_file_size
import random


def extract_filename(path):
    return os.path.basename(path)


def generate_new_filename(ext):
    return f"{uuid.uuid4()}.{ext}"


def get_file_extension(filename):
    return filename.split('.')[-1]


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = (
            'id',
            'name'
        )


class CreateCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ('name',)


class TypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Types
        fields = (
            'id',
            'name'
        )


class CreateTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Types
        fields = ('name',)


class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name', 'photo', 'slug', 'patronymic')


class AdCreateSerializer(serializers.ModelSerializer):
    files = serializers.ListField(child=serializers.CharField(), required=False)

    def generate_unique_order_number(self):
        while True:
            order_number = random.randint(100000, 999999)
            if not Ad.objects.filter(orderNumber=order_number).exists():
                return order_number
    class Meta:
        model = Ad
        fields = (
            'id', 'title',
            'type', 'category', 'deadlineEndAt', 'budget', 'description', 'files'
        )

    def create(self, validated_data):
        types = validated_data.pop('type', [])
        categories = validated_data.pop('category', [])
        file_paths = validated_data.pop('files', [])
        validated_data['orderNumber'] = self.generate_unique_order_number()

        slug = slugify(validated_data['title'])
        ad = Ad.objects.create(**validated_data, slug=slug)
        ad.type.set(types)
        ad.category.set(categories)

        for file_path in file_paths:
            try:
                scan = UploadedFileScan.objects.get(file_path=file_path)
                if scan.was_deleted:
                    continue

                if not default_storage.exists(file_path):
                    raise ValidationError(f"Файл {file_path} не найден в хранилище")

                with default_storage.open(file_path, 'rb') as f:
                    content = f.read()

                original_name = extract_filename(file_path)
                ext = original_name.split('.')[-1]
                new_filename = f"{uuid.uuid4()}.{ext}"

                ad_file_instance = AdFile(ad=ad, scan=scan)
                ad_file_instance.file.save(new_filename, ContentFile(content), save=True)

                scan.file_path = ad_file_instance.file.name
                scan.save()

                default_storage.delete(file_path)

            except UploadedFileScan.DoesNotExist:
                raise ValidationError(f"Файл с путем {file_path} не найден или не был загружен")

        return ad

    def update(self, instance, validated_data):
        file_paths = validated_data.pop('files', None)
        types = validated_data.pop('type', None)
        categories = validated_data.pop('category', None)

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.budget = validated_data.get('budget', instance.budget)
        instance.contact_info = validated_data.get('contact_info', instance.contact_info)
        instance.deadlineEndAt = validated_data.get('deadlineEndAt', instance.deadlineEndAt)
        instance.save()

        if types is not None:
            instance.type.set(types)
        if categories is not None:
            instance.category.set(categories)

        if file_paths is not None:
            AdFile.objects.filter(ad=instance).delete()

            for file_path in file_paths:
                try:
                    scan = UploadedFileScan.objects.get(file_path=file_path)
                    if scan.was_deleted:
                        continue

                    if not default_storage.exists(file_path):
                        raise ValidationError(f"Файл {file_path} не найден в хранилище")

                    with default_storage.open(file_path, 'rb') as f:
                        content = f.read()

                    original_name = extract_filename(file_path)
                    ext = get_file_extension(original_name)
                    new_filename = generate_new_filename(ext)

                    ad_file_instance = AdFile(ad=instance, scan=scan)
                    ad_file_instance.file.save(new_filename, ContentFile(content), save=True)

                    scan.file_path = ad_file_instance.file.name
                    scan.save()

                    default_storage.delete(file_path)

                except UploadedFileScan.DoesNotExist:
                    raise ValidationError(f"Файл с путем {file_path} не найден или не был загружен")

        return instance

    def validate_budget(self, value):
        if value < 1:
            raise serializers.ValidationError("Бюджет должен быть положительным числом")
        if value > 100_000_000:
            raise serializers.ValidationError("Слишком большой бюджет — максимум 100 млн")
        return value



class AdResponseSerializer(serializers.ModelSerializer):
    responder = UserResponseSerializer(read_only=True)

    class Meta:
        model = AdResponse
        fields = ('id', 'responder', 'response_comment')


class AdFileSerializer(serializers.ModelSerializer):
    original_filename = serializers.SerializerMethodField()
    mime_type = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    formatted_file_size = serializers.SerializerMethodField()

    class Meta:
        model = AdFile
        fields = ('id', 'file', 'original_filename', 'mime_type', 'file_size', 'formatted_file_size')

    def get_original_filename(self, obj):
        if obj.scan:
            return obj.scan.original_filename
        return None

    def get_mime_type(self, obj):
        if obj.scan:
            return obj.scan.mime_type
        return None

    def get_file_size(self, obj):
        try:
            return obj.file.size
        except Exception:
            return None

    def get_formatted_file_size(self, obj):
        size = self.get_file_size(obj)
        return format_file_size(size) if size is not None else None


class AdGetSerializer(serializers.ModelSerializer):
    author = UserResponseSerializer(read_only=True)
    responders = AdResponseSerializer(source='adresponse_set', many=True, read_only=True)
    executor = UserResponseSerializer(read_only=True)
    files = AdFileSerializer(many=True, read_only=True)
    type = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    category = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    room_id = serializers.SerializerMethodField()

    class Meta:
        model = Ad
        fields = (
            'id', 'executor', 'orderNumber', 'responders', 'title',
            'type', 'category', 'status', 'deadlineStartAt',
            'deadlineEndAt', 'budget', 'description',
            'author', 'files', 'room_id',
        )

    def get_room_id(self, obj):
        user = self.context['request'].user
        if user.is_authenticated and (obj.author == user or obj.executor == user):
            return getattr(obj, 'room_id', None)
        return None
