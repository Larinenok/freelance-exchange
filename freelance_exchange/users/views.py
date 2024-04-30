import uuid

from decouple import config
from django.contrib.auth.tokens import default_token_generator
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView, RetrieveAPIView, \
    CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, UntypedToken
from .serializers import ListUserInfo, DetailUserProfile, UserPutSerializer, PhotoPatch, UserLoginSerializer, \
    UserRegistrationSerializer, CustomUserSerializer, SkillsSerializer, PasswordResetRequestSerializer, \
    PasswordResetConfirmSerializer, TempUserRegistrationSerializer, ChangePasswordSerializer
from rest_framework import generics, status, permissions, request
from .models import *
#from ads.models import *
#from stars.models import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from pytils.translit import slugify

from datetime import datetime
from django.contrib.auth import get_user_model


User = get_user_model()


class APIUser(ListAPIView):
    permission_classes = [permissions.IsAdminUser, ]
    queryset = CustomUser.objects.all()
    serializer_class = ListUserInfo


class DetailUserView(RetrieveUpdateDestroyAPIView):
    serializer_class = DetailUserProfile
    permission_classes = [IsAuthenticated, ]
    queryset = CustomUser.objects.all()

    def get_object(self):
        return self.request.user

    @swagger_auto_schema(request_body=UserPutSerializer)
    def put(self, request, *args, **kwargs):
        self.serializer_class = UserPutSerializer
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(request_body=PhotoPatch)
    def patch(self, request, *args, **kwargs):
        self.serializer_class = PhotoPatch
        return self.update(request, *args, **kwargs)


class UserLoginAPIView(GenericAPIView):
    permission_classes = [permissions.AllowAny, ]
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            errors = []
            for field, messages in e.detail.items():
                error = {
                    "type": field,
                    "error": messages[0] if isinstance(messages, list) else messages
                }
                errors.append(error)
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data

        if not user.is_approved:
            raise AuthenticationFailed('Этот аккаунт еще не подтвержден.')

        token = RefreshToken.for_user(user)
        data = CustomUserSerializer(user).data
        data["tokens"] = {"refresh": str(token), "access": str(token.access_token)}
        return Response(data, status=status.HTTP_200_OK)


def create_confirmation_token(user):
    token = AccessToken.for_user(user)
    token['username'] = user.username
    token['is_confirmation_token'] = True
    return str(token)


class UserRegistrationAPIView(APIView):
    permission_classes = [AllowAny, ]

    @swagger_auto_schema(request_body=TempUserRegistrationSerializer)
    def post(self, request):
        serializer = TempUserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            temp_user = serializer.save()
            self.send_verification_email(temp_user, request)
            return Response({"message": "Пользователь успешно создан"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_verification_email(self, user, request):
        token = create_confirmation_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        link = f'https://um-stud.ru/activate?uidb64={uid}&token={token}'
        full_link = link
        subject = "Подтверждение учетной записи"
        message = f"Пожалуйста, перейдите по следующей ссылке, чтобы активировать вашу учетную запись: {full_link}"
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])


class ActivateAccountView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
        uidb64 = kwargs.get('uidb64')
        token = kwargs.get('token')
        try:
            token = AccessToken(token)
            if not token['is_confirmation_token']:
                raise Exception("Некорректный тип токена")

            uid = urlsafe_base64_decode(uidb64).decode()
            temp_user = TemporaryUserData.objects.get(pk=uid)

            if not CustomUser.objects.filter(username=temp_user.username).exists():
                user = CustomUser.objects.create(
                    username=temp_user.username,
                    email=temp_user.email,
                    first_name=temp_user.first_name,
                    last_name=temp_user.last_name,
                    is_approved=True
                )
                user.set_password(temp_user.password)
                user.save()

                temp_user.delete()
                return Response({"message": "Аккаунт активирован"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Аккаунт уже активирован"}, status=status.HTTP_200_OK)

        except TemporaryUserData.DoesNotExist:
            return Response({"error": "Неверный токен или пользователь уже активирован"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def create_confirmation_token_for_reset_password(user):
    token = RefreshToken.for_user(user)
    token['is_confirmation_token'] = True
    return str(token.access_token)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=PasswordResetRequestSerializer)
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            token = create_confirmation_token_for_reset_password(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            link = f'https://um-stud.ru/auth/reset?uidb64={uid}&token={token}'
            full_link = link
            subject = "Сброс пароля"
            message = f"Пожалуйста, перейдите по ссылке, чтобы сбросить ваш пароль: {full_link}"
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
            return Response({'message': 'Инструкции по сбросу пароля отправлены на вашу почту.'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=PasswordResetConfirmSerializer)
    def post(self, request, uidb64, token):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
            try:
                UntypedToken(token)
            except (InvalidToken, TokenError) as e:
                raise ValueError("Недействительный токен")
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Недействительный токен или UID.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Ваш пароль успешно изменен.'}, status=status.HTTP_200_OK)


class UserProfileView(RetrieveAPIView):
    serializer_class = DetailUserProfile
    permission_classes = [IsAuthenticated, ]
    queryset = CustomUser.objects.all()
    lookup_field = 'slug'

    def get_object(self):
        slug = self.kwargs.get("slug")
        return get_object_or_404(CustomUser, slug=slug)


class SkillChangeView(ListAPIView):
    permission_classes = [AllowAny, ]
    queryset = Skills.objects.all()
    serializer_class = SkillsSerializer


class ChangePasswordView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=ChangePasswordSerializer)
    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response({"message": "Пароль успешно изменен."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
