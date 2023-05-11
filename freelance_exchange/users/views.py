from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer, RegisterSerializer, AdSerializer
from .serializers import RegisterSerializer, AdSerializer
from rest_framework import generics
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
        profiles.append({'user': user, 'token': Token.objects.get_or_create(user=user)[0], 'stars': StarsJson.parse(user.stars_freelancer)})

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
    ad = get_object_or_404(Ad, slug=slug_name)
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


@api_view(['GET'])
def get_all_users_stars(request):
        users = CustomUser.objects.all()
        stars = []

        for user in users:
            stars.append({
                'username': user.username,
                'stars': StarsJson.parse(user.stars_freelancer)
            })

        return Response(stars)


@api_view(['GET'])
def get_user_stars(request, username):
    user = get_object_or_404(CustomUser, slug=username)

    return Response(StarsJson.parse(user.stars_freelancer))

@api_view(['POST'])
def set_user_stars(request, username):
    try:
        whose = request.POST['whose']
        value = request.POST['value']
    except:
        return Response('Require "whose" and "value" parameters', status='401')

    user = get_object_or_404(CustomUser, slug=username)
    _stars = json.dumps(StarsJson.add_star(user.stars_freelancer, username=whose, value=value))
    user.stars_freelancer = _stars
    user.save()

    return Response({'result': '_stars'})

@api_view(['POST'])
def delete_user_stars(request, who, whose):
    user = get_object_or_404(CustomUser, slug=who)
    _stars = json.dumps(StarsJson.remove_star(user.stars_freelancer, username=whose))
    user.stars_freelancer = _stars
    user.save()

    return Response({'result': _stars})


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
