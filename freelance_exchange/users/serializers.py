import re

from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from .models import *


from django.contrib.auth import get_user_model, authenticate
from stars.models import Star
from stars.serializers import ListStarInfo

User = get_user_model()


class ListUserInfo(serializers.ModelSerializer):
    email = serializers.EmailField()
    skills = serializers.StringRelatedField(many=True)
    birth_date = serializers.DateField(format='%d.%m.%Y', input_formats=['%d.%m.%Y',])
    stars = serializers.SerializerMethodField()

    def get_stars(self, obj):
        return round(obj.stars or 0, 2)

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'username',
            'slug',
            'is_superuser',
            'is_staff',
            'first_name',
            'last_name',
            'patronymic',
            'email',
            'phone',
            'place_study_work',
            'skills',
            'birth_date',
            'description',
            'language',
            'photo',
            'views',
            'stars',
        )


class SkillsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skills
        fields = (
            'id',
            'name'
        )


class CreateSkillsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skills
        fields = ('name',)


class CustomUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email'
        )


class PortfolioItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioItem
        fields = (
            'id',
            'user',
            'title',
            'description',
            'file',
            'uploaded_at'
        )


class DetailUserProfile(serializers.ModelSerializer):
    email = serializers.EmailField()
    skills = SkillsSerializer(many=True, read_only=True)
    birth_date = serializers.DateField(format='%d.%m.%Y', input_formats=['%d.%m.%Y', ])
    portfolio_items = PortfolioItemSerializer(many=True, read_only=True)
    stars = serializers.SerializerMethodField()
    ratings = serializers.SerializerMethodField()
    completed_ads_count = serializers.SerializerMethodField()

    def get_stars(self, obj):
        return round(obj.stars or 0, 2)

    def get_ratings(self, obj):
        ratings = Star.objects.filter(target=obj)
        return ListStarInfo(ratings, many=True).data

    def get_completed_ads_count(self, obj):
        return obj.ads_executor.filter(status='completed').count()

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'username',
            'slug',
            'is_superuser',
            'is_staff',
            'first_name',
            'last_name',
            'patronymic',
            'email',
            'phone',
            'place_study_work',
            'skills',
            'birth_date',
            'description',
            'language',
            'photo',
            'views',
            'stars',
            'ratings',
            'portfolio_items',
            'completed_ads_count',
        )


class UserPutSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    birth_date = serializers.DateField(format='%d.%m.%Y', input_formats=['%d.%m.%Y', ])

    class Meta:
        model = CustomUser
        fields = (
            'first_name',
            'last_name',
            'patronymic',
            'email',
            'skills',
            'birth_date',
            'place_study_work',
            'description',
            'phone',
            'photo'
        )


class PhotoPatch(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'photo',
        )


class UserLoginSerializer(serializers.Serializer):
    login_or_email = serializers.CharField(label="Логин или Email")
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        login_or_email = data.get('login_or_email')
        password = data.get('password')

        if not login_or_email or not password:
            raise serializers.ValidationError({
                'login_or_email': "Должен быть указан 'login_or_email'.",
                'password': "Должен быть указан 'password'."
            })

        user = User.objects.filter(username=login_or_email).first() or User.objects.filter(email=login_or_email).first()

        if user is None:
            raise serializers.ValidationError({
                'login_or_email': "Неверный логин или пароль",
                'password': "Неверный логин или пароль"
            })

        if not authenticate(username=user.username, password=password):
            raise serializers.ValidationError({
                'login_or_email': "Неверный логин или пароль",
                'password': "Неверный логин или пароль"
            })

        return user


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']

    def validate_username(self, value):
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError("Логин может содержать только латинские буквы, цифры и подчеркивания.")
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})

        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "Логин пользователя уже занят."})

        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "Этот email уже используется."})

        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователя с таким email не существует.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    confirm_password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Пароли не совпадают."})
        return data


class TempUserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = TemporaryUserData
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']

    def validate_username(self, value):
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError("Логин может содержать только латинские буквы, цифры и подчеркивания.")
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})

        if CustomUser.objects.filter(username=data['username']).exists() or TemporaryUserData.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "Имя пользователя уже занято."})

        if CustomUser.objects.filter(email=data['email']).exists() or TemporaryUserData.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "Этот email уже используется."})

        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        hashed_password = make_password(validated_data['password'])
        validated_data['password'] = hashed_password
        return TemporaryUserData.objects.create(**validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password_confirm = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Старый пароль неверен.")
        return value

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "Новые пароли не совпадают."})
        validate_password(data['new_password'])
        return data


class SimpleUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'id',
            'slug',
            'first_name',
            'last_name',
            'patronymic',
            'photo'
        )
        read_only_fields = fields


class BlacklistSerializer(serializers.ModelSerializer):
    blocked_user = SimpleUserProfileSerializer(read_only=True)

    class Meta:
        model = BlackList
        fields = (
            'id',
            'blocked_user',
            'created_at'
        )
        read_only_fields = ['id', 'created_at']


class CreateBlacklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlackList
        fields = ['blocked_user']


class UserListForUsersSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    skills = serializers.StringRelatedField(many=True)
    birth_date = serializers.DateField(format='%d.%m.%Y', input_formats=['%d.%m.%Y', ])

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'slug',
            'is_superuser',
            'is_staff',
            'first_name',
            'last_name',
            'patronymic',
            'email',
            'phone',
            'place_study_work',
            'skills',
            'birth_date',
            'description',
            'language',
            'photo',
            'views',
            'stars',
        )



