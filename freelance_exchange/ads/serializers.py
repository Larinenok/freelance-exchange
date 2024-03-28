from django.conf import settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from pytils.translit import slugify

from .models import *


class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = ('id', 'author', 'title', 'description', 'category', 'type', 'budget', 'pub_date', 'contact_info')
        def create(self, validated_data):
            ad = Ad.objects.create(
                author=validated_data['author'],
                title=validated_data['title'],
                id=validated_data['id'],
                slug=slugify(validated_data['username']),
                description=validated_data['description'],
                category=validated_data['category'],
                type=validated_data['type'],
                budget=validated_data['budget'],
                contact_info=validated_data['contact_info'],
            )


class AdFileSerializer(serializers.ModelSerializer):
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
