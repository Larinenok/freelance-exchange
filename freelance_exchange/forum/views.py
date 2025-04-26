from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Discussion, Comment
from .serializers import DiscussionSerializer, DiscussionCreateSerializer, CommentSerializer, CommentCreateSerializer, \
    DiscussionUpdateStatusSerializer, DiscussionMarkCommentSerializer


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
