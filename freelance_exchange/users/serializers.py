from django.conf import settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from pytils.translit import slugify

from .models import *


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)

        # Add custom claims
        token['username'] = user.username
        return token


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'username', 'password', 'password2', 'email', 'photo', 'description', 'language', 'birth_date')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'photo': {'required': False},
            'description': {'required': False},
            'language': {'required': False},
            'birth_date': {'required': False},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        description = ''
        language = settings.LANGUAGE_CODE
        photo = 'default/default.jpg'

        if ('description' in validated_data.keys()):
            description = validated_data['description']

        if ('language' in validated_data.keys()):
            language=validated_data['language'],

        if ('language' in validated_data.keys()):
            photo=validated_data['photo'],

        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            slug=slugify(validated_data['username']),
            description=description,
            language=language,
            photo=photo,
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = ('id', 'author', 'title', 'description', 'category', 'budget', 'pub_date', 'contact_info')
        def create(self, validated_data):
            ad = Ad.objects.create(
                author=validated_data['author'],
                title=validated_data['title'],
                id=validated_data['id'],
                slug=slugify(validated_data['username']),
                description=validated_data['description'],
                category=validated_data['category'],
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
