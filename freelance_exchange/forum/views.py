import uuid
import logging
import requests
from decouple import config
from django.conf import settings
from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import Discussion, Comment
from .serializers import DiscussionSerializer, DiscussionCreateSerializer, CommentSerializer, CommentCreateSerializer, \
    DiscussionUpdateStatusSerializer, DiscussionMarkCommentSerializer, FileUploadSerializer


logger = logging.getLogger(__name__)

class DiscussionListView(generics.ListAPIView):
    queryset = Discussion.objects.all()
    serializer_class = DiscussionSerializer
    permission_classes = [permissions.AllowAny]


class DiscussionCreateView(generics.CreateAPIView):
    serializer_class = DiscussionCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class DiscussionDetailView(generics.RetrieveAPIView):
    queryset = Discussion.objects.all()
    serializer_class = DiscussionSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        discussion_id = self.kwargs.get('discussion_id')
        discussion = generics.get_object_or_404(Discussion, id=discussion_id)
        serializer.save(author=self.request.user, discussion=discussion)


class CommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        discussion_id = self.kwargs.get('discussion_id')
        return Comment.objects.filter(discussion__id=discussion_id)


class DiscussionUpdateStatusView(generics.UpdateAPIView):
    queryset = Discussion.objects.all()
    serializer_class = DiscussionUpdateStatusSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Discussion.objects.filter(author=self.request.user)


class DiscussionMarkCommentView(generics.UpdateAPIView):
    queryset = Discussion.objects.all()
    serializer_class = DiscussionMarkCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        discussion = super().get_object()
        if discussion.author != self.request.user:
            self.permission_denied(
                self.request,
                message="Вы не являетесь автором этого обсуждения."
            )
        return discussion

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        discussion = self.get_object()

        serializer = self.get_serializer(discussion, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({"status": "Комментарий отмечен как решающий"}, status=status.HTTP_200_OK)


class FileUploadView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FileUploadSerializer
    parser_classes = [MultiPartParser]

    VIRUSTOTAL_API_KEY = config('API_KEY_VISUALTOTAL')

    MAX_FILE_SIZE = 32 * 1024 * 1024

    @swagger_auto_schema(
        request_body=FileUploadSerializer,
        responses={201: openapi.Response('File uploaded successfully', FileUploadSerializer)}
    )

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        upload_type = request.data.get('type')

        if not file or not upload_type:
            return Response({'error': 'Файл или тип не переданы.'}, status=status.HTTP_400_BAD_REQUEST)

        ext = file.name.split('.')[-1]
        filename = f"{uuid.uuid4()}.{ext}"

        if upload_type == "chat":
            path = f"temp_upload/chat_files/{filename}"
        elif upload_type == "discussion":
            path = f"temp_upload/forum/{filename}"
        else:
            return Response({'error': "Неверный тип загрузки."}, status=status.HTTP_400_BAD_REQUEST)

        saved_path = default_storage.save(path, ContentFile(file.read()))
        file_url = default_storage.url(saved_path)

        if file.size > self.MAX_FILE_SIZE:
            safety_check_result = self.check_file_safety_with_url(file_url)
            if safety_check_result:
                return Response({'file_url': file_url, 'status': 'File is safe'}, status=status.HTTP_201_CREATED)
            else:
                default_storage.delete(saved_path)
                return Response({'error': 'File is dangerous'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if self.check_file_safety(file):
                return Response({'file_url': file_url, 'status': 'File is safe'}, status=status.HTTP_201_CREATED)
            else:
                default_storage.delete(saved_path)
                return Response({'error': 'File is dangerous'}, status=status.HTTP_400_BAD_REQUEST)

    def check_file_safety(self, file):
        url = "https://www.virustotal.com/api/v3/files"
        headers = {
            "accept": "application/json",
            "x-apikey": self.VIRUSTOTAL_API_KEY,
        }

        logger.info(f"Отправка файла {file.name} на VirusTotal...")

        files = {'file': (file.name, file, file.content_type)}

        response = requests.post(url, headers=headers, files=files)

        logger.info(f"Ответ от VirusTotal: {response.status_code}, {response.text}")

        if response.status_code == 200:
            result = response.json()
            analysis_id = result.get("data", {}).get("id")
            return self.check_analysis_status(analysis_id)
        else:
            logger.error(f"Ошибка при отправке файла: {response.status_code}, {response.text}")
            return False

    def check_file_safety_with_url(self, file_url):
        url = "https://www.virustotal.com/api/v3/files/upload_url"
        headers = {
            "accept": "application/json",
            "x-apikey": self.VIRUSTOTAL_API_KEY,
        }

        data = {'url': file_url}

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            result = response.json()
            analysis_id = result.get("data", {}).get("id")
            return self.check_analysis_status(analysis_id)
        else:
            return False

    def check_analysis_status(self, analysis_id):
        url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
        headers = {
            "accept": "application/json",
            "x-apikey": self.VIRUSTOTAL_API_KEY,
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            result = response.json()
            attributes = result.get("data", {}).get("attributes", {})
            if attributes.get("status") == "completed":
                stats = attributes.get("stats", {})
                if stats.get("malicious", 0) > 0:
                    return False
                else:
                    return True
            else:
                return False
        else:
            return False

class FileDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        try:
            file_url = request.data.get('file_url')

            if not file_url:
                return Response({'error': 'Не передана ссылка на файл'}, status=status.HTTP_400_BAD_REQUEST)

            file_path = file_url.replace(settings.MEDIA_URL, "")

            if default_storage.exists(file_path):
                default_storage.delete(file_path)
                return Response({'message': 'Файл удалён.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Файл не найден.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
