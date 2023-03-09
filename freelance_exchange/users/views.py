from django.shortcuts import render
from .models import *


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def home_view(request):
    profiles = CustomUser.objects.all()

    context = {
        'profiles' : profiles,
    }
    for p in profiles:
        print(p.photo)

    return render(request, 'home.html', context)


def post_view(request, slug):
    user = CustomUser.objects.get(slug=slug)

    ip = get_client_ip(request)

    if Ip.objects.filter(ip=ip).exists():
        user.views.add(Ip.objects.get(ip=ip))
    else:
        Ip.objects.create(ip=ip)
        user.views.add(Ip.objects.get(ip=ip))  
    
    context = {
        'user' : user,
    }
    return render(request, 'main/post.html', context)
