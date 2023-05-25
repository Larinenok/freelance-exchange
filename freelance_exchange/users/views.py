from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer, RegisterSerializer, AdSerializer, AdFileSerializer
from rest_framework import generics, status
from django.views.generic.edit import FormView
from .forms import AdForm, UserForm
from .models import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from pytils.translit import slugify


#################
# @api_view(['POST'])
# def signup(request):
#     data = request.data
#     serializer = RegisterSerializer(data=data)
#     if serializer.is_valid():
#         if not CustomUser.objects.filter(username=data['email']).exists():
#             user = CustomUser.objects.create(first_name=data['first_name'], last_name=data['last_name'], username=data['email'], email=data['email'], password=data['password'])
#             user.save()
#             # student = Student.objects.create(auth=user, name=data['first_name'], email=data['email'])
#             return Response({'message':'User Created Successfully'}, status=status.HTTP_201_CREATED)
#         else:
#             return Response({'message':'User Already Exists'}, status=status.HTTP_400_BAD_REQUEST)
#     else:
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
# @api_view(['GET'])
# def signin(request):
#     data = request.data
#
#     if CustomUser.objects.filter(username=data['username']).exists():
#         user = CustomUser.objects.get(username=data['username'])
#         if user.check_password(data['password']):
#             return Response(RegisterSerializer(instance=user).data, status=status.HTTP_200_OK)
#         else:
#             return Response({'message':'Invalid Password'}, status=status.HTTP_400_BAD_REQUEST)
#     else:
#         return Response({'message':'User Does Not Exist'}, status=status.HTTP_400_BAD_REQUEST)
#################


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
        'user': request.user,
        'profiles': profiles,
    }

    return render(request, 'home.html', context)

def terms_of_service(request):
    return render(request, 'terms_of_service.html')

def me(request):
    token = request.headers['Authorization']

    if (request.user.isauthenticated()):
        return profile(request, request.user.slug)
    
    return Response('Not logged in.')


def all_ads(request):
    ads = []
    for ad in Ad.objects.all():
        ads.append({'ad': ad})

    context = {
        'ads': ads,
    }
    return render(request, 'all_ads.html', context)


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


@api_view(['GET'])
def get_all_users_stars(request):
        users = CustomUser.objects.all()
        stars = []

        for user in users:
            stars.append({
                'username': user.slug,
                'stars': StarsJson.parse(user.stars_freelancer)
            })

        return Response(stars)


@api_view(['GET'])
def get_user_stars(request, username):
    try:
        user = get_object_or_404(CustomUser, slug=username)

        return Response(StarsJson.parse(user.stars_freelancer))
    except:
        return Response('''Username not found''', status='401')


@swagger_auto_schema(method='put', manual_parameters=[
    openapi.Parameter('whose', openapi.IN_QUERY, description='Whose review are we deleting', type=openapi.TYPE_STRING),
    openapi.Parameter('value', openapi.IN_QUERY, description='Number of stars (from 0 to 5)', type=openapi.TYPE_INTEGER)
])
@api_view(['PUT'])
@permission_classes([permissions.IsAdminUser])
def set_user_stars(request, username):
    try:
        whose = str(request.query_params.get('whose'))
        value = int(request.query_params.get('value'))
    except:
        return Response('''Require "whose" and "value" parameters''', status='401')

    try:
        user = get_object_or_404(CustomUser, slug=str(username))
        stars = json.dumps(StarsJson.add_star(user.stars_freelancer, username=whose, value=value))
        user.stars_freelancer = stars
        user.save()

        return Response({'result': stars})
    except:
        return Response('''Username not found''', status='401')


@swagger_auto_schema(method='delete', manual_parameters=[
    openapi.Parameter('whose', openapi.IN_QUERY, description='Whose review are we deleting', type=openapi.TYPE_STRING)
])
@api_view(['DELETE'])
@permission_classes([permissions.IsAdminUser])
def delete_user_stars(request, username):
    try:
        whose = str(request.query_params.get('whose'))
    except:
        return Response('''Require "whose" parameter''', status='401')

    try:
        user = get_object_or_404(CustomUser, slug=username)
        _stars = json.dumps(StarsJson.remove_star(user.stars_freelancer, username=whose))
        user.stars_freelancer = _stars
        user.save()

        return Response({'result': _stars})
    except:
        return Response('''Username not found''', status='401')


@swagger_auto_schema(method='post', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'title': openapi.Schema(type=openapi.TYPE_STRING, description='Title of the Ad'),
        'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description of the Ad'),
        'category': openapi.Schema(type=openapi.TYPE_STRING, description='Category of the Ad'),
        'budget': openapi.Schema(type=openapi.TYPE_INTEGER, description='Budget of the Ad'),
        'contact_info': openapi.Schema(type=openapi.TYPE_STRING, description='Contact information for the Ad'),
        'slug': openapi.Schema(type=openapi.TYPE_STRING, description='Slug'),
        'files': openapi.Schema(type=openapi.TYPE_FILE, description='Files of the Ad'),
    }
))
@api_view(['POST'])
def create_ad(request):
    author = request.user
    title = request.data.get('title')
    description = request.data.get('description')
    budget = request.data.get('budget')
    category = request.data.get('category')
    contact_info = request.data.get('contact_info')
    ad = Ad.objects.create(
        author=author,
        title=title,
        slug=slugify(title),
        description=description,
        category=category,
        budget=budget,
        contact_info=contact_info,
    )
    ad.save()
    return Response({'message': 'Ad created successfully'})


@swagger_auto_schema(method='delete', manual_parameters=[openapi.Parameter('id', openapi.IN_QUERY, description='ID of the Ad', type=openapi.TYPE_INTEGER)])
@api_view(['DELETE'])
@permission_classes([permissions.IsAdminUser])
def delete_ad(request):
    ad_id = request.query_params.get('id')
    try:
        ad = Ad.objects.get(id=ad_id)
        ad.delete()
        return Response({'message': 'Ad deleted successfully!'})
    except Ad.DoesNotExist:
        return Response({'error': 'Ad not found!'}, status=404)


@swagger_auto_schema(method='put', manual_parameters=[openapi.Parameter('id', openapi.IN_QUERY, description='ID of the Ad', type=openapi.TYPE_INTEGER)], request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'title': openapi.Schema(type=openapi.TYPE_STRING, description='Title of the Ad'),
        'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description of the Ad'),
        'category': openapi.Schema(type=openapi.TYPE_STRING, description='Category of the Ad'),
        'budget': openapi.Schema(type=openapi.TYPE_INTEGER, description='Budget of the Ad'),
        'contact_info': openapi.Schema(type=openapi.TYPE_STRING, description='Contact information for the Ad'),
        'slug': openapi.Schema(type=openapi.TYPE_STRING, description='Slug'),
    }
))
@api_view(['PUT'])
@permission_classes([permissions.IsAdminUser])
def edit_ad(request):
    ad_id = request.query_params.get('id')
    try:
        ad = Ad.objects.get(id=ad_id)
        author = request.user
        title = request.data.get('title', ad.title)
        description = request.data.get('description', ad.description)
        category = request.data.get('category', ad.category)
        budget = request.data.get('budget', ad.budget)
        contact_info = request.data.get('contact_info', ad.contact_info)

        ad.author = author
        ad.title = title
        ad.slug = slugify(title)
        ad.description = description
        ad.category = category
        ad.budget = budget
        ad.contact_info = contact_info
        ad.save()

        return Response({'message': 'Ad updated successfully!'})
    except Ad.DoesNotExist:
        return Response({'error': 'Ad not found!'}, status=404)


class AdFileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = AdFileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)


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
