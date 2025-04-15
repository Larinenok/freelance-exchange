from drf_yasg import openapi
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveDestroyAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from users.models import *
from ads.models import *
from .models import *
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions
from .serializers import *
from users.models import CustomUser


class APIStar(ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Star.objects.all()
    serializer_class = ListStarInfo


class GetByUsernameAPIStar(GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ListStarInfo

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(
            'username',
            openapi.IN_PATH,
            description="Username пользователя, для которого нужно получить отзывы",
            type=openapi.TYPE_STRING,
            required=True
        )
    ])
    def get(self, request, username, *args, **kwargs):
        try:
            target_user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

        stars = Star.objects.filter(target=target_user)
        data = ListStarInfo(stars, many=True).data
        return Response(data, status=status.HTTP_200_OK)


class StarChangeAPIView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangeStarSerializer

    @swagger_auto_schema(request_body=ChangeStarSerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Отзыв успешно сохранен'}, status=status.HTTP_201_CREATED)


class StarRetrieveDestroyAPIView(RetrieveDestroyAPIView):
    queryset = Star.objects.all()
    serializer_class = ListStarInfo

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def delete(self, request, *args, **kwargs):
        star = self.get_object()
        if star.author != request.user:
            raise PermissionDenied("Вы не можете удалить отзыв, который не создавали.")
        response = super().delete(request, *args, **kwargs)
        update_user_rating(star.target)
        return response


