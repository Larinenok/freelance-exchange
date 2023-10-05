from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes, permission_classes
# from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenRefreshSerializer, TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from .serializers import MyTokenObtainPairSerializer, RegisterSerializer, AdSerializer, AdFileSerializer
from rest_framework import generics, status
from django.views.generic.edit import FormView
from .forms import AdForm, UserForm
from .models import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from pytils.translit import slugify
# from .settings import api_settings
from rest_framework.settings import api_settings

from datetime import datetime


def check_token(request):
    try:
        token = request.headers['Authorization']
        if 'Bearer' in token:
            token = token[7:]
        user_id = AccessToken(token)['user_id']
        return CustomUser.objects.get(id=user_id)
    except:
        return None


#                             #
# -------- register --------- #
#                             #
@swagger_auto_schema(method='post',
    operation_id="register",
    manual_parameters=[
        openapi.Parameter('first_name', openapi.IN_QUERY, description='first_name', type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('last_name', openapi.IN_QUERY, description='last_name', type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('username', openapi.IN_QUERY, description='username', type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('password', openapi.IN_QUERY, description='password', type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('password2', openapi.IN_QUERY, description='password verification', type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('email', openapi.IN_QUERY, description='email', type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('photo', openapi.IN_FORM, description='profile picture', type=openapi.TYPE_FILE, required=False),
        openapi.Parameter('description', openapi.IN_QUERY, description='description', type=openapi.TYPE_STRING, required=False),
        openapi.Parameter('language', openapi.IN_QUERY, description='language', type=openapi.TYPE_STRING, required=False),
        openapi.Parameter('birth_date', openapi.IN_QUERY, description='birth date', type=openapi.FORMAT_DATE, required=False),
])
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def signup(request):
    if request.data.get('password') is not None:
        data = request.data
    else:
        data = request.query_params

    # исправить поле др по умолчанию
    serializer = RegisterSerializer(data=data)
    if serializer.is_valid():
        if not CustomUser.objects.filter(username=data['email']).exists():
            try:
                birth = datetime.strptime(data['birth_date'], '%d.%m.%Y').strftime('%Y-%m-%d')
            except:
                birth = None
            try:
                user = CustomUser.objects.create(first_name=data['first_name'], last_name=data['last_name'], username=data['username'], slug=slugify(data['username']), email=data['email'], password=data['password'], photo=request.FILES.get('photo', 'default/default.jpg'), birth_date=birth)
                user.set_password(user.password)
                user.save()
                refresh = RefreshToken.for_user(user)
                return Response({'refresh' : str(refresh), 'access': str(refresh.access_token)}, status=status.HTTP_201_CREATED)
            except:
                return Response({'message':'Login Already Exists'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':'User Already Exists'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#                             #
# ---------- login ---------- #
#                             #
@swagger_auto_schema(method='post', manual_parameters=[
    openapi.Parameter('username', openapi.IN_QUERY, description='username', type=openapi.TYPE_STRING, required=False),
    openapi.Parameter('email', openapi.IN_QUERY, description='email', type=openapi.TYPE_STRING, required=False),
    openapi.Parameter('password', openapi.IN_QUERY, description='password', type=openapi.TYPE_STRING),
])
@api_view(['POST'])
def signin(request):
    if request.data.get('password') is not None:
        data = request.data
    else:
        data = request.query_params

    if data.get('username') is None and data.get('email') is None:
        return Response({'message':'Require username or email'}, status=status.HTTP_400_BAD_REQUEST)

    if data.get('username') is not None:
        if CustomUser.objects.filter(username=data.get('username')).exists():
            user = CustomUser.objects.get(username=data.get('username'))
        else:
            return Response({'message':'User Does Not Exist'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        if CustomUser.objects.filter(email=data.get('email')).exists():
            user = CustomUser.objects.get(email=data.get('email'))
        else:
            return Response({'message':'User Does Not Exist'}, status=status.HTTP_400_BAD_REQUEST)

    if user.check_password(data['password']):
        refresh = RefreshToken.for_user(user)
        return Response({'refresh' : str(refresh), 'access': str(refresh.access_token)}, status=status.HTTP_200_OK)
    else:
        return Response({'message':'Invalid Password'}, status=status.HTTP_400_BAD_REQUEST)


#                             #
# --------- refresh --------- #
#                             #
@swagger_auto_schema(method='post', manual_parameters=[
    openapi.Parameter('refresh', openapi.IN_QUERY, description='refresh token', type=openapi.TYPE_STRING, required=True),
])
@api_view(['POST'])
def get_access_token(request):
    if request.data.get('password') is not None:
        data = request.data
    else:
        data = request.query_params

    return Response(str(RefreshToken(data.get('refresh'))))


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@swagger_auto_schema(method='get')
@api_view(['GET'])
def get_users(request):
    profiles = []

    for user in CustomUser.objects.all():
        try:
            birth = datetime.strptime(str(user.birth_date), '%Y-%m-%d').strftime('%d.%m.%Y')
        except:
            birth = None

        profiles.append({
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'slug': user.slug,
            'birth_date': birth,
            'photo': user.photo.name,
            'description': user.description,
            'language': user.language,
            # 'views': user.views,
            'stars': StarsJson.parse(user.stars_freelancer)
        })

    return Response({'users': profiles}, status=status.HTTP_201_CREATED)


def home_view(request):
    profiles = []

    for user in CustomUser.objects.all():
        profiles.append({'user': user, 'stars': StarsJson.parse(user.stars_freelancer)})

    context = {
        'user': request.user,
        'profiles': profiles,
    }

    return render(request, 'home.html', context)

def terms_of_service(request):
    return render(request, 'terms_of_service.html')

def me(request):
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
    }
    return render(request, 'profile.html', context)

def ad_view(request, id):
    stop = id.find('-')
    if stop != -1:
        id = id[:stop]
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


@swagger_auto_schema(method='get', manual_parameters=[
    openapi.Parameter('username', openapi.IN_PATH, description='Whose review are we checking', type=openapi.TYPE_STRING, required=True)
])
@api_view(['GET'])
def get_user_stars(request, username):
    try:
        user = get_object_or_404(CustomUser, slug=username)

        return Response(StarsJson.parse(user.stars_freelancer))
    except:
        return Response('''Username not found''', status='401')


@swagger_auto_schema(method='put', manual_parameters=[
    openapi.Parameter('whose', openapi.IN_QUERY, description='Whose review are we deleting', type=openapi.TYPE_STRING, required=True),
    openapi.Parameter('value', openapi.IN_QUERY, description='Number of stars (from 0 to 5)', type=openapi.TYPE_INTEGER, required=True)
])
@api_view(['PUT'])
def set_user_stars(request, username):
    try:
        whose = str(request.data.get('whose'))
        value = int(request.data.get('value'))
    except:
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
            whose = str(request.data.get('whose'))
    except:
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

#                             #
# ----------- ads ----------- #
#                             #
@swagger_auto_schema(method='post', manual_parameters=[
        openapi.Parameter('title', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Title of the Ad', required=True),
        openapi.Parameter('description', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Description of the Ad', required=True),
        openapi.Parameter('category', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Category of the Ad', required=True),
        openapi.Parameter('budget', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Budget of the Ad', required=True),
        openapi.Parameter('contact_info', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Contact information for the Ad', required=True),
        openapi.Parameter('files', openapi.IN_QUERY, type=openapi.TYPE_FILE, description='Files of the Ad', required=True),
])
@api_view(['POST'])
def create_ad(request):
    author = check_token(request)
    if not author:
        return Response('Non authorized', status=status.HTTP_401_UNAUTHORIZED)

    try:
        title = request.query_params.get('title')
        description = request.query_params.get('description')
        budget = request.query_params.get('budget')
        category = request.query_params.get('category')
        contact_info = request.query_params.get('contact_info')
    except:
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
def delete_ad(request):
    user = check_token(request)
    if not user:
        return Response('Non authorized', status=status.HTTP_401_UNAUTHORIZED)

    ad_id = request.query_params.get('id')
    try:
        ad = Ad.objects.get(id=ad_id)
        if ad.author != user:
            return Response({'error': 'You must be author'}, status=status.HTTP_401_UNAUTHORIZED)
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
def edit_ad(request):
    author = check_token(request)
    if not author:
        return Response('Non authorized', status=status.HTTP_401_UNAUTHORIZED)

    ad_id = request.query_params.get('id')
    try:
        ad = Ad.objects.get(id=ad_id)

        try:
            title = request.query_params.get('title', ad.title)
            description = request.query_params.get('description', ad.description)
            category = request.query_params.get('category', ad.category)
            budget = request.query_params.get('budget', ad.budget)
            contact_info = request.query_params.get('contact_info', ad.contact_info)
        except:
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
