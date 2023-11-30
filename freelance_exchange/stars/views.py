from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from users.models import *
from ads.models import *
from stars.models import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(method='get', operation_description='Get all stars')
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
