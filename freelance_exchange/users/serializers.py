from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from .models import *

from django.contrib.auth import get_user_model, authenticate

User = get_user_model()


class ListUserInfo(serializers.ModelSerializer):
    email = serializers.EmailField()
    skills = serializers.StringRelatedField(many=True)
    birth_date = serializers.DateField(format='%d.%m.%Y', input_formats=['%d.%m.%Y',])

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'username',
            'slug',
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
            # 'stars_freelancer',
            # 'stars_customer',
        )


class SkillsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skills
        fields = (
            'id',
            'name'
        )


class CustomUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email'
        )


class DetailUserProfile(serializers.ModelSerializer):
    email = serializers.EmailField()
    skills = SkillsSerializer(many=True, read_only=True)
    birth_date = serializers.DateField(format='%d.%m.%Y', input_formats=['%d.%m.%Y', ])

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'slug',
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
            # 'stars_freelancer',
            # 'stars_customer',
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
                'login_or_email': "Неверный логин или пароль"
            })

        if not authenticate(username=user.username, password=password):
            raise serializers.ValidationError({
                'password': "Неверный логин или пароль"
            })

        return user


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
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



