from django.shortcuts import get_object_or_404
from rest_framework import generics, status, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from pytils.translit import slugify

from .models import Ad, AdFile, AdResponse
from .serializers import *
from chat.models import ChatRoom
from users.models import BlackList
from django.db.models import Subquery, OuterRef, IntegerField, Q


class TypeChangeView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny, ]
    queryset = Types.objects.all()
    serializer_class = TypesSerializer


class CreateTypesView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Types.objects.all()
    serializer_class = CreateTypesSerializer

    def perform_create(self, serializer):
        serializer.save()

    def post(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            many = True
        else:
            many = False

        serializer = self.get_serializer(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)



class CategoryChangeView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny, ]
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer


class CreateCategoriesView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Categories.objects.all()
    serializer_class = CreateCategoriesSerializer

    def perform_create(self, serializer):
        serializer.save()

    def post(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            many = True
        else:
            many = False

        serializer = self.get_serializer(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class AdListCreateView(generics.ListCreateAPIView):
    def get_queryset(self):
        queryset = Ad.objects.exclude(status__in=[Ad.CLOSED, Ad.COMPLETED])

        user = self.request.user
        if user.is_authenticated:
            blocked_by_users = BlackList.objects.filter(blocked_user=user).values_list('owner', flat=True)

            blocked_users = BlackList.objects.filter(owner=user).values_list('blocked_user', flat=True)

            queryset = queryset.exclude(author__id__in=blocked_by_users)
            queryset = queryset.exclude(author__id__in=blocked_users)

            chat_subquery = ChatRoom.objects.filter(ad=OuterRef('pk'), participants=user).values('id')[:1]

            queryset = queryset.annotate(room_id=Subquery(chat_subquery, output_field=IntegerField()))

        return queryset.select_related('author', 'executor') \
            .prefetch_related('type', 'category', 'files', 'responders', 'chat_rooms')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AdCreateSerializer
        return AdGetSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        create_serializer = self.get_serializer(data=request.data)
        create_serializer.is_valid(raise_exception=True)
        ad = create_serializer.save(author=request.user)

        response_serializer = AdGetSerializer(ad, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class AdDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Ad.objects.all()

        user = self.request.user
        if user.is_authenticated:
            blocked_by_users = BlackList.objects.filter(blocked_user=user).values_list('owner', flat=True)
            blocked_users = BlackList.objects.filter(owner=user).values_list('blocked_user', flat=True)

            queryset = queryset.exclude(author__id__in=blocked_by_users)
            queryset = queryset.exclude(author__id__in=blocked_users)

            chat_subquery = ChatRoom.objects.filter(ad=OuterRef('pk'), participants=user).values('id')[:1]
            queryset = queryset.annotate(room_id=Subquery(chat_subquery, output_field=IntegerField()))

        return queryset.select_related('author', 'executor') \
            .prefetch_related('type', 'category', 'files', 'responders', 'chat_rooms')

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return AdCreateSerializer
        return AdGetSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        read_serializer = AdGetSerializer(instance, context={'request': request})
        return Response(read_serializer.data)

    # def get_object(self):
    #     ad = super().get_object()
    #     return ad


class AdFileListView(generics.ListAPIView):
    queryset = AdFile.objects.all()
    serializer_class = AdFileSerializer
    permission_classes = [permissions.IsAuthenticated]


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
    serializer_class = AdGetSerializer
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
        return Ad.objects.filter(executor=self.request.user, status=Ad.IN_PROGRESS)


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

        ChatRoom.objects.filter(ad=ad).update(is_closed=True)

        return Response({'message': 'Ad closed successfully and related chats were closed.'}, status=status.HTTP_200_OK)

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


class MyWorkListView(generics.ListAPIView):
    serializer_class = AdGetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Ad.objects.filter(executor=user, status=Ad.IN_PROGRESS).order_by('-deadlineEndAt')


class CustomerArchiveView(generics.ListAPIView):
    serializer_class = AdGetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ad.objects.filter(author=self.request.user, status__in=[Ad.CLOSED, Ad.COMPLETED]).order_by('-closed_date')


class ExecutorArchiveView(generics.ListAPIView):
    serializer_class = AdGetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ad.objects.filter(executor=self.request.user, status__in=[Ad.CLOSED, Ad.COMPLETED]).order_by('-closed_date')


class CompletedAdsView(generics.ListAPIView):
    serializer_class = AdCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ad.objects.filter(executor=self.request.user, status=Ad.COMPLETED)


class ExecutorStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Ad.objects.filter(executor=request.user, status=Ad.COMPLETED).count()
        return Response({"completed_ads_count": count})

