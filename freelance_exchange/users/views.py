from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from .serializers import ListUserInfo, DetailUserProfile, UserPutSerializer, PhotoPatch, UserLoginSerializer, \
    UserRegistrationSerializer, CustomUserSerializer, SkillsSerializer
from rest_framework import generics, status, permissions
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
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        token = RefreshToken.for_user(user)
        data = CustomUserSerializer(user).data
        data["tokens"] = {"refresh": str(token), "access": str(token.access_token)}
        return Response(data, status=status.HTTP_200_OK)


class UserRegistrationAPIView(APIView):
    permission_classes = [AllowAny, ]

    @swagger_auto_schema(request_body=UserRegistrationSerializer)
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Пользователь успешно создан"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
