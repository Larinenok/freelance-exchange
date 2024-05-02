from rest_framework import status
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from .models import Discussion, Comment
from .serializers import DiscussionSerializer, CommentSerializer
from django.shortcuts import get_object_or_404


@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter('title', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Title of the discussion', required=True),
        openapi.Parameter('description', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Description of the discussion', required=True),
    ],
    responses={201: DiscussionSerializer()},
)
@api_view(['post'])
def create_discussion(request):
    if not request.user:
        return Response('Non authorized', status=status.HTTP_401_UNAUTHORIZED)

    try:
        title = request.query_params.get('title')
        description = request.query_params.get('description')
    except:
        title = request.data.get('title')
        description = request.data.get('description')

    serializer = DiscussionSerializer(data={
        'title': title,
        'description': description,
        'author': request.user.id})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='ID of the discussion', required=True),
    ],
    responses={200: DiscussionSerializer()},
)
@api_view(['get'])
def get_discussion(request):
    if not request.user:
        return Response('Non authorized', status=status.HTTP_401_UNAUTHORIZED)
    discussion_id = request.query_params.get('id')
    discussion = get_object_or_404(Discussion, pk=discussion_id)
    serializer = DiscussionSerializer(discussion)
    return Response(serializer.data)

@swagger_auto_schema(
    method='put',
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='ID of the discussion', required=True),
        openapi.Parameter('title', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='New title of the discussion'),
        openapi.Parameter('description', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='New description of the discussion'),
    ],
    responses={200: DiscussionSerializer()},
)
@api_view(['put'])
def update_discussion(request):
    if not request.user:
        return Response('Non authorized', status=status.HTTP_401_UNAUTHORIZED)
    discussion_id = request.query_params.get('id')
    discussion = get_object_or_404(Discussion, pk=discussion_id)
    if request.user != discussion.author:
        return Response({'error': 'You must be author'}, status=status.HTTP_401_UNAUTHORIZED)

    title = request.query_params.get('title')
    description = request.query_params.get('description')

    serializer = DiscussionSerializer(discussion, data={
        'title': title,
        'description': description},
                                      partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='ID of the discussion', required=True),
    ],
    responses={204: None},
)
@api_view(['post'])
def close_discussion(request):
    if not request.user:
        return Response('Non authorized', status=status.HTTP_401_UNAUTHORIZED)
    discussion_id = request.query_params.get('id')
    discussion = get_object_or_404(Discussion, pk=discussion_id)
    if request.user != discussion.author:
        return Response({'error': 'You must be author'}, status=status.HTTP_401_UNAUTHORIZED)
    discussion.status = Discussion.CLOSED
    return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    method='delete',
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='ID of the discussion', required=True),
    ],
    responses={204: None},
)
@api_view(['delete'])
def delete_discussion(request):
    if not request.user:
        return Response('Non authorized', status=status.HTTP_401_UNAUTHORIZED)
    discussion_id = request.query_params.get('id')
    discussion = get_object_or_404(Discussion, pk=discussion_id)
    if request.user != discussion.author:
        return Response({'error': 'You must be author'}, status=status.HTTP_401_UNAUTHORIZED)
    discussion.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter('text', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Text of the comment', required=True),
    ],
    responses={201: CommentSerializer()},
)
@api_view(['post'])
def create_comment(request):
    if not request.user:
        return Response('Non authorized', status=status.HTTP_401_UNAUTHORIZED)

    try:
        text = request.query_params.get('text')
    except:
        text = request.data.get('text')

    serializer = CommentSerializer(data={'text': text, 'author': request.user.id})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='ID of the comment', required=True),
    ],
    responses={200: CommentSerializer()},
)
@api_view(['get'])
def get_comment(request):
    if not request.user:
        return Response('Non authorized', status=status.HTTP_401_UNAUTHORIZED)
    comment_id = request.query_params.get('id')
    comment = get_object_or_404(Comment, pk=comment_id)
    serializer = CommentSerializer(comment)
    return Response(serializer.data)

@swagger_auto_schema(
    method='put',
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='ID of the comment', required=True),
        openapi.Parameter('text', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='New text of the comment'),
    ],
    responses={200: CommentSerializer()},
)
@api_view(['put'])
def update_comment(request):
    if not request.user:
        return Response('Non authorized', status=status.HTTP_401_UNAUTHORIZED)
    comment_id = request.query_params.get('id')
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        return Response({'error': 'You must be author'}, status=status.HTTP_401_UNAUTHORIZED)

    text = request.query_params.get('text')

    serializer = CommentSerializer(comment, data={'text': text}, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='delete',
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='ID of the comment', required=True),
    ],
    responses={204: None},
)
@api_view(['delete'])
def delete_comment(request):
    if not request.user:
        return Response('Non authorized', status=status.HTTP_401_UNAUTHORIZED)
    comment_id = request.query_params.get('id')
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        return Response({'error': 'You must be author'}, status=status.HTTP_401_UNAUTHORIZED)
    comment.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)