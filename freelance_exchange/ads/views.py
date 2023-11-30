from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import AdSerializer, AdFileSerializer
from rest_framework import generics, status
from .models import *
from users.views import check_token
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from pytils.translit import slugify


# def all_ads(request):
#     ads = []
#     for ad in Ad.objects.all():
#         ads.append({'ad': ad})
#
#     context = {
#         'ads': ads,
#     }
#     return render(request, 'all_ads.html', context)

@swagger_auto_schema(method='get', operation_description='Get all ads')
@api_view(['GET'])
def all_ads(request):
    ads = []
    for ad in Ad.objects.all():
        files = AdFile.objects.filter(ad=ad.id)
        ads.append({'ad': {
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
        }})

    context = {
        'ads': ads,
    }

    return Response(context, status=status.HTTP_200_OK)


@swagger_auto_schema(method='post',
    operation_description="get_ad",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, title='ID of the Ad'),
        },
        required=['id']
    ),
    responses={
        status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ad': openapi.Schema(type=openapi.TYPE_STRING, title='The Ad'),
})})
@api_view(['POST'])
def api_ad_view(request):
    if request.data.get('id') is not None:
        data = request.data
    else:
        data = request.query_params

    try:
        ad = Ad.objects.get(id=data.get('id'))
    except:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    files = AdFile.objects.filter(ad=data.get(ad))
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


def ad_view(request, id, slug):
    ad = get_object_or_404(Ad, id=id)
    slug = ad.slug
    files = AdFile.objects.filter(ad=ad)
    context = {
        'ad': ad,
        'files': files,
    }
    return render(request, 'ad_view.html', context)


@swagger_auto_schema(method='post',
    operation_description="create_ad",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'title': openapi.Schema(type=openapi.TYPE_STRING, title='Title of the Ad'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, title='Description of the Ad'),
            'category': openapi.Schema(type=openapi.TYPE_STRING, title='Category of the Ad'),
            'budget': openapi.Schema(type=openapi.TYPE_INTEGER, title='Budget of the Ad'),
            'contact_info': openapi.Schema(type=openapi.TYPE_STRING, title='Contact information for the Ad'),
            'files': openapi.Schema(type=openapi.TYPE_FILE, title='Files of the Ad'),
        },
        required=['title', 'description', 'category', 'budget', 'contact_info']
    ),
    responses={
        status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, title='Result of creation the Ad'),
})})
@api_view(['POST'])
def create_ad(request):
    author = check_token(request)
    if not author:
        return Response({'error': 'Non authorized'}, status=status.HTTP_401_UNAUTHORIZED)

    if request.data.get('title') is not None:
        data = request.data
    else:
        data = request.query_params

    title = data.get('title')
    description = data.get('description')
    budget = data.get('budget')
    category = data.get('category')
    contact_info = data.get('contact_info')

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


@swagger_auto_schema(method='delete',
    operation_description="Delete the Ad",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, title='Title of the Ad'),
        },
        required=['id']
    ),
    responses={
        status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, title='Result of deletion the Ad'),
})})
@api_view(['DELETE'])
def delete_ad(request):
    user = check_token(request)
    if not user:
        return Response({'error': 'Non authorized'}, status=status.HTTP_401_UNAUTHORIZED)

    if request.data.get('id') is not None:
        data = request.data
    else:
        data = request.query_params

    try:
        ad = Ad.objects.get(id=data.get('id'))
        if ad.author != user:
            return Response({'error': 'You must be author'}, status=status.HTTP_401_UNAUTHORIZED)
        ad.delete()
        return Response({'message': 'Ad deleted successfully!'})
    except Ad.DoesNotExist:
        return Response({'error': 'Ad not found!'}, status=404)


@swagger_auto_schema(method='post',
    operation_description="Response the Ad",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, title='Title of the Ad'),
            'comment': openapi.Schema(type=openapi.TYPE_STRING, title='Response comment to Ad'),
        },
        required=['id', 'comment']
    ),
    responses={
        status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, title='Result of deletion the Ad'),
})})
@api_view(['POST'])
def response_ad(request):
    user = check_token(request)
    if not user:
        return Response({'error': 'Non authorized'}, status=status.HTTP_401_UNAUTHORIZED)

    if request.data.get('id') is not None:
        data = request.data
    else:
        data = request.query_params

    try:
        ad = Ad.objects.get(id=data.get('id'))
        ad_response = AdResponse.objects.create(
            ad=ad,
            responder=user,
            response_comment=data.get('comment')
        )
        ad_response.save()
        return Response({'message': 'Response sent!'})
    except Ad.DoesNotExist:
        return Response({'error': 'Ad not found!'}, status=404)


@swagger_auto_schema(method='post',
    operation_description="Responses the Ads",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, title='Title of the Ad'),
        },
        required=['id']
    ),
    responses={
        status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'responses': openapi.Schema(type=openapi.TYPE_STRING, title='Responses'),
})})
@api_view(['post'])
def get_responses(request):
    responses = []
    user = check_token(request)
    if not user:
        return Response({'error': 'Non authorized'}, status=status.HTTP_401_UNAUTHORIZED)

    if request.data.get('id') is not None:
        data = request.data
    else:
        data = request.query_params

    try:
        ad = Ad.objects.get(id=data.get('id'))
        if ad.author != user:
            return Response({'error': 'You must be author'}, status=status.HTTP_401_UNAUTHORIZED)
        for response in AdResponse.objects.filter(ad=ad):
            responses.append({
                'response_id': response.id,
                'username': response.responder.username,
                'slug': response.responder.slug,
                'comment': response.response_comment,
                'first_name': response.responder.first_name,
            })
        return Response({'responses': responses}, status=status.HTTP_201_CREATED)
    except Ad.DoesNotExist:
        return Response({'error': 'Ad not found!'}, status=404)


@swagger_auto_schema(method='post',
    operation_description="Set executor to the Ads",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'ad_id': openapi.Schema(type=openapi.TYPE_INTEGER, title='ID of the Ad'),
            'response_id': openapi.Schema(type=openapi.TYPE_INTEGER, title='ID of the Response'),
        },
        required=['ad_id', 'response_id']
    ),
    responses={
        status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, title='Result'),
})})
@api_view(['post'])
def set_executor(request):
    user = check_token(request)
    if not user:
        return Response({'error': 'Non authorized'}, status=status.HTTP_401_UNAUTHORIZED)

    if request.data.get('id') is not None:
        data = request.data
    else:
        data = request.query_params

    try:
        ad = Ad.objects.get(id=data.get('ad_id'))
        response = AdResponse.objects.get(id=data.get('response_id'))
        if ad.author != user:
            return Response({'error': 'You must be author'}, status=status.HTTP_401_UNAUTHORIZED)
        if response.ad == ad:
            ad.executor = response.responder
            ad.save()
            return Response({'Executor set successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'There is no response with this id for ad'}, status=status.HTTP_201_CREATED)
    except Ad.DoesNotExist:
        return Response({'error': 'Ad not found!'}, status=404)


@swagger_auto_schema(method='put',
    operation_description="Edit the Ad",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, title='ID of the Ad'),
            'title': openapi.Schema(type=openapi.TYPE_STRING, title='Title of the Ad'),
            'description': openapi.Schema(type=openapi.TYPE_STRING, title='Description of the Ad'),
            'category': openapi.Schema(type=openapi.TYPE_STRING, title='Category of the Ad'),
            'budget': openapi.Schema(type=openapi.TYPE_INTEGER, title='Budget of the Ad'),
            'contact_info': openapi.Schema(type=openapi.TYPE_STRING, title='Contact information of the Ad'),
            'files': openapi.Schema(type=openapi.TYPE_FILE, title='Files of the Ad'),
        },
        required=['ad_id', 'response_id']
    ),
    responses={
        status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, title='Result'),
})})
@api_view(['PUT'])
def edit_ad(request):
    author = check_token(request)
    if not author:
        return Response({'error': 'Non authorized'}, status=status.HTTP_401_UNAUTHORIZED)

    if request.data.get('id') is not None:
        data = request.data
    else:
        data = request.query_params

    try:
        ad = Ad.objects.get(id=data.get('id'))

        title = data.get('title', ad.title)
        description = data.get('description', ad.description)
        category = data.get('category', ad.category)
        budget = data.get('budget', ad.budget)
        contact_info = data.get('contact_info', ad.contact_info)

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


class AdList(generics.ListCreateAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
