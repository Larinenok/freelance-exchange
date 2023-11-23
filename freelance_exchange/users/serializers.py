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

        if ('photo' in validated_data.keys()):
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
