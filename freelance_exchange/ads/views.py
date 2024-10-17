from django.shortcuts import get_object_or_404
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from pytils.translit import slugify

from .models import Ad, AdFile, AdResponse
from .serializers import *

class AdListCreateView(generics.ListCreateAPIView):
    queryset = Ad.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AdCreateSerializer  # Используем для POST
        return AdGetSerializer  # Используем для GET

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class AdDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ad.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method != 'GET':
            return AdCreateSerializer  # Используем для всего остального
        return AdGetSerializer  # Используем для GET

    # def perform_update(self, serializer):
    #     serializer.save(slug=slugify(serializer.validated_data['title']))

class AdFileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = AdFileUploadSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('ad_id', in_=openapi.IN_FORM, type=openapi.TYPE_INTEGER, description='ID of the Ad', required=True),
            openapi.Parameter('files', in_=openapi.IN_FORM, type=openapi.TYPE_FILE, description='Files to upload', required=True, multiple=True),
        ]
    )
    def post(self, request, *args, **kwargs):
        user = request.user

        # Проверка авторизации
        if not user or not user.is_authenticated:
            return Response({'error': 'You must be authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        # Получаем ad_id и проверяем его наличие
        ad_id = request.data.get('ad_id')
        if not ad_id:
            return Response({'error': 'ad_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Получаем объявление
        ad = get_object_or_404(Ad, id=ad_id)

        # Проверка прав пользователя
        if ad.author != user and not user.is_superuser:
            return Response({'error': 'You must be the author or a superuser'}, status=status.HTTP_403_FORBIDDEN)

        # Получаем файлы из запроса
        files = request.FILES.getlist('files')
        if not files:
            return Response({'error': 'At least one file is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Создаем файлы через сериализатор
        serializer = self.serializer_class(data={'files': files})
        if serializer.is_valid():
            ad_files = serializer.save()

            # Привязываем загруженные файлы к объявлению
            for ad_file in ad_files:
                ad.files.add(ad_file)

            return Response({'message': 'Files added successfully'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdFileListView(generics.ListAPIView):
    queryset = AdFile.objects.all()
    serializer_class = AdFileSerializer
    permission_classes = [permissions.IsAuthenticated]

class AdFileDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'file_id': openapi.Schema(type=openapi.TYPE_INTEGER),
        }
    ))
    def delete(self, request, *args, **kwargs):
        file_id = request.query_params.get('file_id')
        if not file_id:
            return Response({'error': 'File ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        file = get_object_or_404(AdFile, id=file_id)
        file.delete()
        return Response({'message': 'File deleted successfully'}, status=status.HTTP_200_OK)

class AdResponseView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'ad_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'comment': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ))
    def post(self, request, *args, **kwargs):
        ad_id = request.data.get('ad_id')
        comment = request.data.get('comment')

        if not ad_id:
            return Response({'error': 'Ad ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        ad = get_object_or_404(Ad, id=ad_id)
        if ad.status != Ad.OPEN:
            return Response({'error': 'This Ad is not open'}, status=status.HTTP_400_BAD_REQUEST)

        response = AdResponse.objects.create(
            ad=ad,
            responder=request.user,
            response_comment=comment
        )
        return Response({'message': 'Response sent!'}, status=status.HTTP_201_CREATED)

class AdExecutorView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'ad_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'response_id': openapi.Schema(type=openapi.TYPE_INTEGER),
        }
    ))
    def post(self, request, *args, **kwargs):
        ad_id = request.data.get('ad_id')
        response_id = request.data.get('response_id')

        if not ad_id or not response_id:
            return Response({'error': 'Ad ID and Response ID are required'}, status=status.HTTP_400_BAD_REQUEST)

        ad = get_object_or_404(Ad, id=ad_id)
        response = get_object_or_404(AdResponse, id=response_id)

        if ad.author != request.user and not request.user.is_superuser:
            return Response({'error': 'You must be author'}, status=status.HTTP_401_UNAUTHORIZED)

        if response.ad != ad:
            return Response({'error': 'There is no response with this ID for the ad'}, status=status.HTTP_400_BAD_REQUEST)

        ad.executor = response.responder
        ad.status = Ad.IN_PROGRESS
        ad.save()

        return Response({'message': 'Executor set successfully'}, status=status.HTTP_200_OK)

class UserAdsView(generics.ListAPIView):
    serializer_class = AdCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ad.objects.filter(author=self.request.user)

class UserClosedAdsView(generics.ListAPIView):
    serializer_class = AdCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ad.objects.filter(executor=self.request.user, status=Ad.CLOSED)

class AdsInProgressView(generics.ListAPIView):
    serializer_class = AdCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ad.objects.filter(executor=self.request.user)

class CloseAdView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'ad_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'reason': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ))
    def post(self, request, *args, **kwargs):
        ad_id = request.data.get('ad_id')
        reason = request.data.get('reason')

        if not ad_id:
            return Response({'error': 'Ad ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        ad = get_object_or_404(Ad, id=ad_id)

        if ad.author != request.user and not request.user.is_superuser:
            return Response({'error': 'You must be author'}, status=status.HTTP_401_UNAUTHORIZED)

        ad.status = Ad.CLOSED
        ad.closed_date = timezone.now()
        ad.save()

        return Response({'message': 'Ad closed successfully'}, status=status.HTTP_200_OK)

class DeleteAdView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        }
    ))
    def delete(self, request, *args, **kwargs):
        ad_id = request.query_params.get('id')
        if not ad_id:
            return Response({'error': 'Ad ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        ad = get_object_or_404(Ad, id=ad_id)
        if ad.author != request.user and not request.user.is_superuser:
            return Response({'error': 'You must be author'}, status=status.HTTP_401_UNAUTHORIZED)

        ad.delete()
        return Response({'message': 'Ad deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)

class GetResponsesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('id', openapi.IN_QUERY, description='ID of the Ad', type=openapi.TYPE_INTEGER, required=True)
    ])
    def get(self, request, *args, **kwargs):
        ad_id = request.query_params.get('id')

        if not ad_id:
            return Response({'error': 'Ad ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        ad = get_object_or_404(Ad, id=ad_id)

        if ad.author != request.user and not request.user.is_superuser:
            return Response({'error': 'You must be author'}, status=status.HTTP_401_UNAUTHORIZED)

        responses = AdResponse.objects.filter(ad=ad)
        serializer = AdResponseSerializer(responses, many=True)
        return Response({'responses': serializer.data}, status=status.HTTP_200_OK)
