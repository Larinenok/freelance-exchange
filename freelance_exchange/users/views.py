from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from .serializers import MyTokenObtainPairSerializer, RegisterSerializer
from rest_framework import generics, status
from users.models import *
from ads.models import *
from stars.models import *
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
        'email': user.email,
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
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

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


@swagger_auto_schema(method='get')
@api_view(['GET'])
def get_me(request):
    user = check_token(request)
    if not user:
        return Response({'error': 'Non authorized'}, status=status.HTTP_401_UNAUTHORIZED)

    return Response({'user': user_data(user)}, status=status.HTTP_201_CREATED)


def home_view(request):
    profiles = []

    for user in CustomUser.objects.all():
        profiles.append(user_data(user))

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
    
    return Response({'error': 'Non authorized'})


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
