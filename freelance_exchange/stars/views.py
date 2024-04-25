from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework import status
from users.models import *
from ads.models import *
from stars.models import *
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions

from .models import *
from .serializers import *


class APIStar(ListAPIView):
    permission_classes = [permissions.AllowAny, ]
    queryset = Star.objects.all()
    serializer_class = ListStarInfo


class GetByUsernameAPIStar(GenericAPIView):
    permission_classes = [permissions.AllowAny, ]
    queryset = Star.objects.all()
    serializer_class = InputStarsSerializer

    @swagger_auto_schema(request_body=InputStarsSerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            stars = Star.objects.filter(username=request.data.get('username'))
            stars = GetStarInfo(stars, many=True).data

            return Response({request.data.get('username'): stars}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StarChangeAPIView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = ChangeStarSerializer

    @swagger_auto_schema(request_body=ChangeStarSerializer)
    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = CustomUser.objects.get(username=request.data.get('username'))
            stars = Star.objects.filter(username=request.data.get('username')).all()
            rating = sum(star.count for star in stars)
            if stars.count() > 0:
                user.stars = rating / stars.count()
            user.save()
            return Response({'message': f'Отзыв об пользователе ({request.data.get("username")}) успешно оставлен'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(request_body=ChangeStarSerializer)
    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.delete(request.data)
            user = CustomUser.objects.get(username=request.data.get('username'))
            stars = Star.objects.filter(username=request.data.get('username')).all()
            rating = sum(star.count for star in stars)
            if stars.count() > 0:
                user.stars = rating / stars.count()
            user.save()
            return Response({'message': f'Отзыв об пользователе ({request.data.get("username")}) успешно удален'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
