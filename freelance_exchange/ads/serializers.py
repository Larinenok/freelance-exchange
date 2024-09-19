from django.conf import settings
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from pytils.translit import slugify
from .models import Ad, AdFile, AdResponse


class AdSerializer(serializers.ModelSerializer):
    files = serializers.PrimaryKeyRelatedField(queryset=AdFile.objects.all(), many=True, required=False)

    class Meta:
        model = Ad
        fields = (
            'id', 'title', 'description', 'category', 'type',
            'budget', 'contact_info', 'status', 'files'
        )
        read_only_fields = (
            'author', 'pub_date', 'executor'
        )

    def create(self, validated_data):
        files = validated_data.pop('files', [])
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
