from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from .serializers import MessageCreateSerializer, MessageSerializer


class CreateMessageView(CreateAPIView):
    serializer_class = MessageCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save

        message_serialzier = MessageSerializer(message)
        return Response(message_serialzier.data, status=status.HTTP_201_CREATED)

