from django.shortcuts import render, get_object_or_404
from rest_framework.authtoken.models import Token
from .serializers import MyTokenObtainPairSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
# from django.contrib.auth.models import User
from .serializers import RegisterSerializer, AdSerializer
from rest_framework import generics, status
from django.views.generic.edit import FormView
from .forms import AdForm, UserForm

from .models import *


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def home_view(request):
    profiles = []

    for user in CustomUser.objects.all():
        profiles.append({'user': user, 'token': Token.objects.get_or_create(user=user)[0]})

    context = {
        'profiles': profiles,
    }

    return render(request, 'home.html', context)

def all_ads(request):
    ads = []
    for ad in Ad.objects.all():
        ads.append({'ad': ad})

    context = {
        'ads': ads,
    }
    return render(request, 'user_ads.html', context)

def profile(request, slug_name):
    user = get_object_or_404(CustomUser, slug=slug_name)
    ads = Ad.objects.filter(author__slug=slug_name)
    files = AdFile.objects.filter(ad__in=ads)
    context = {
        'profile': user,
        'ads': ads,
        'files': files,
        'token': Token.objects.get_or_create(user=user)[0],
    }
    return render(request, 'profile.html', context)

def ad_view(request, id, slug_name):
    ad = get_object_or_404(Ad, id=id)
    files = AdFile.objects.filter(ad=ad)
    context = {
        'ad': ad,
        'files': files,
    }
    return render(request, 'ad_view.html', context)

def post_view(request, slug_name):
    user = get_object_or_404(CustomUser, slug=slug_name)
    host = request.META["HTTP_HOST"]
    ip = request.META["REMOTE_ADDR"]
    user_agent = request.META["HTTP_USER_AGENT"]
    path = request.path
    if Ip.objects.filter(ip=ip).exists():
        user.views.add(Ip.objects.get(ip=ip))
    else:
        Ip.objects.create(ip=ip)
        user.views.add(Ip.objects.get(ip=ip))

    context = {
        'user': user,
        'host': host,
        'ip': ip,
        'user agent': user_agent,
        'path': path,
    }
    return render(request, 'meta.html', context)


class MyObtainTokenPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class AdList(generics.ListCreateAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
