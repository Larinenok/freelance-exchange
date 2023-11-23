from django.shortcuts import render, get_object_or_404
from rest_framework import generics, permissions, viewsets
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


token_responses = {
    status.HTTP_200_OK: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'access': openapi.Schema(type=openapi.TYPE_STRING, title='access token'),
            'refresh': openapi.Schema(type=openapi.TYPE_STRING, title='refresh token'),
})}


def user_data(user) -> dict:
    try:
        birth = datetime.strptime(str(user.birth_date), '%Y-%m-%d').strftime('%d.%m.%Y')
    except:
        birth = None

    return {
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
    }


#                             #
# -------- register --------- #
#                             #
@swagger_auto_schema(method='post',
    operation_id="register",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'first_name': openapi.Schema(type=openapi.TYPE_STRING, title='first name'),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING, title='last name'),
            'username': openapi.Schema(type=openapi.TYPE_STRING, title='username'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, title='password'),
            'password2': openapi.Schema(type=openapi.TYPE_STRING, title='password verification'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, title='email'),
            'photo': openapi.Schema(type=openapi.TYPE_FILE, title='profile picture'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, title='description'),
            'language': openapi.Schema(type=openapi.TYPE_STRING, title='language', enum=settings.LANGUAGES),
            'birth_date': openapi.Schema(type=openapi.TYPE_STRING, title='birth date', format='DD.MM.YYYY'),
        },
        required=['first_name', 'last_name', 'username', 'password', 'password2', 'email']
    ),
    responses=token_responses
)
@api_view(['POST'])
@permission_classes([AllowAny,])
def signup(request):
    if request.data.get('password') is not None:
        data = request.data
    else:
        data = request.query_params

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
                return Response({'refresh' : str(refresh), 'access': str(refresh.access_token), 'user': user_data(user)}, status=status.HTTP_201_CREATED)
            except:
                return Response({'message':'Login Already Exists'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':'User Already Exists'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#                             #
# ---------- login ---------- #
#                             #
@swagger_auto_schema(method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'login': openapi.Schema(type=openapi.TYPE_STRING, title='email or username'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, title='password'),
        },
        required=['login', 'password']
    ),
    responses=token_responses
)
@api_view(['POST'])
def signin(request):
    if request.data.get('password') is not None:
        data = request.data
    else:
        data = request.query_params

    login = data.get('login')

    if not '@' in login:
        if CustomUser.objects.filter(username=login).exists():
            user = CustomUser.objects.get(username=login)
        else:
            return Response({'message':'User Does Not Exist'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        if CustomUser.objects.filter(email=login).exists():
            user = CustomUser.objects.get(email=login)
        else:
            return Response({'message':'User Does Not Exist'}, status=status.HTTP_400_BAD_REQUEST)

    if user.check_password(data['password']):
        refresh = RefreshToken.for_user(user)
        return Response({'refresh' : str(refresh), 'access': str(refresh.access_token), 'user': user_data(user)}, status=status.HTTP_200_OK)
    else:
        return Response({'message':'Invalid Password'}, status=status.HTTP_400_BAD_REQUEST)


#                             #
# --------- refresh --------- #
#                             #
@swagger_auto_schema(method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'refresh': openapi.Schema(type=openapi.TYPE_STRING, title='refresh token'),
        }
    ),
    responses={
        status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'access': openapi.Schema(type=openapi.TYPE_STRING, title='access token'),
})})
@api_view(['POST'])
def get_access_token(request):
    try:
        data = request.data
    except:
        data = request.query_params

    try:
        access = RefreshToken(data.get('refresh'))
    except:
        return Response({'message':'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'access': str(access)}, status=status.HTTP_200_OK)


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
        profiles.append(user_data(user))

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


# @swagger_auto_schema(method='get', manual_parameters=[
#         openapi.Parameter('id', openapi.IN_QUERY, description='id', type=openapi.TYPE_INTEGER, required=True),
# ])
@api_view(['GET'])
def api_ad_view(request, id):
    ad = get_object_or_404(Ad, id=id)
    files = AdFile.objects.filter(ad=ad)
    context = {
        'author': ad.author.first_name,
        'title': ad.title,
        'id': ad.id,
        'slug': ad.slug,
        'description': ad.description,
        'category': ad.category,
        'budget': ad.budget,
        'pub_date': ad.pub_date,
        'contact_info': ad.contact_info,
        'files': files,
    }

    return Response(context, status=status.HTTP_200_OK)


def ad_view(request, id):
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
    user_by_token = check_token(request)
    if not user_by_token:
        return Response('Non authorized', status=status.HTTP_401_UNAUTHORIZED)

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

        if user != user_by_token:
            return Response('''You can only change your reviews''', status=status.HTTP_401_UNAUTHORIZED)

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
def delete_user_stars(request, username):
    user_by_token = check_token(request)
    if not user_by_token:
        return Response('Non authorized', status=status.HTTP_401_UNAUTHORIZED)

    try:
        whose = str(request.data.get('whose'))
        if whose == 'None':
            raise Exception('')
    except:
        try:
            whose = str(request.query_params.get('whose'))
        except:
            return Response('''Require "whose" parameter''', status='401')

    try:
        user = get_object_or_404(CustomUser, slug=username)

        if user != user_by_token:
            return Response('''You can only change your reviews''', status=status.HTTP_401_UNAUTHORIZED)

        stars = json.dumps(StarsJson.remove_star(user.stars_freelancer, username=whose))
        user.stars_freelancer = stars
        user.save()

        return Response({'result': stars})
    except:
        return Response('''Non-correct data''', status='401')

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
