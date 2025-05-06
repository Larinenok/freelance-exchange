import mimetypes
import time
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
from .models import Discussion, Comment, UploadedFileScan
from .serializers import DiscussionSerializer, DiscussionCreateSerializer, CommentSerializer, CommentCreateSerializer, \
    DiscussionUpdateStatusSerializer, DiscussionMarkCommentSerializer, FileUploadSerializer, UploadedFileScanSerializer
from users.tasks import start_file_scan_virustotal


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

    @swagger_auto_schema(request_body=CommentCreateSerializer)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        discussion_id = self.kwargs.get('discussion_id')
        discussion = generics.get_object_or_404(Discussion, id=discussion_id)
        serializer.save()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        discussion_id = self.kwargs.get('discussion_id')
        context['discussion'] = generics.get_object_or_404(Discussion, id=discussion_id)
        return context


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
        if getattr(self, 'swagger_fake_view', False):
            return Discussion.objects.none()

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

    SAFE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'pptx', 'xlsx', 'pdf']

    @swagger_auto_schema(
        request_body=FileUploadSerializer,
        responses={201: openapi.Response('File uploaded successfully', FileUploadSerializer)}
    )

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        upload_type = request.data.get('type')

        if not file or not upload_type:
            return Response({'error': 'Файл или тип не переданы.'}, status=status.HTTP_400_BAD_REQUEST)

        ext = file.name.split('.')[-1].lower()
        filename = f"{uuid.uuid4()}.{ext}"

        if upload_type == "chat":
            path = f"temp_upload/chat_files/{filename}"
        elif upload_type == "discussion":
            path = f"temp_upload/forum/{filename}"
        elif upload_type == "comment":
            path = f"temp_upload/forum/comment/{filename}"
        elif upload_type == "ad":
            path = f"temp_upload/ad/{filename}"
        else:
            return Response({'error': "Неверный тип загрузки."}, status=status.HTTP_400_BAD_REQUEST)

        saved_path = default_storage.save(path, ContentFile(file.read()))
        file_url = default_storage.url(saved_path)

        original_filename = file.name

        mime_type, _ = mimetypes.guess_type(original_filename)
        mime_type = mime_type or 'application/octet-stream'

        if ext in self.SAFE_EXTENSIONS:
            scan = UploadedFileScan.objects.create(
                file_path=saved_path,
                status="safe",
                was_deleted=False,
                original_filename=original_filename,
                mime_type=mime_type
            )
        else:
            scan = UploadedFileScan.objects.create(
                file_path=saved_path,
                status="pending",
                original_filename=original_filename,
                mime_type=mime_type
            )

            start_file_scan_virustotal.delay(scan.id, file.name, saved_path)

        if scan.was_deleted:
            file_url = None

        return Response({
            'file_url': file_url,
            'file_path': saved_path,
            'scan_status': scan.status,
            'scan_id': scan.id,
            'was_deleted': scan.was_deleted,
            'original_filename': original_filename,
            'mime_type': mime_type
        }, status=status.HTTP_201_CREATED)


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


class FileScanStatusView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = UploadedFileScan.objects.all()
    serializer_class = UploadedFileScanSerializer
    lookup_field = 'id'
