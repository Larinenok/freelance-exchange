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


def all_ads(request):
    ads = []
    for ad in Ad.objects.all():
        ads.append({'ad': ad})

    context = {
        'ads': ads,
    }
    return render(request, 'all_ads.html', context)


@swagger_auto_schema(method='get', manual_parameters=[
        openapi.Parameter('id', openapi.IN_QUERY, description='id', type=openapi.TYPE_INTEGER, required=True),
])
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


def ad_view(request, id, slug):
    ad = get_object_or_404(Ad, id=id)
    slug = ad.slug
    files = AdFile.objects.filter(ad=ad)
    context = {
        'ad': ad,
        'files': files,
    }
    return render(request, 'ad_view.html', context)



#                             #
# ----------- ads ----------- #
#                             #
@swagger_auto_schema(method='post', manual_parameters=[
    openapi.Parameter('title', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Title of the Ad',
                      required=True),
    openapi.Parameter('description', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Description of the Ad',
                      required=True),
    openapi.Parameter('category', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Category of the Ad',
                      required=True),
    openapi.Parameter('budget', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Budget of the Ad',
                      required=True),
    openapi.Parameter('contact_info', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                      description='Contact information for the Ad', required=True),
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


@swagger_auto_schema(method='delete', manual_parameters=[
    openapi.Parameter('id', openapi.IN_QUERY, description='ID of the Ad', type=openapi.TYPE_INTEGER)])
@api_view(['DELETE'])
def delete_ad(request):
    user = check_token(request)
    if not user:
        return Response('Non authorized', status=status.HTTP_401_UNAUTHORIZED)

    id = request.query_params.get('id')
    try:
        ad = Ad.objects.get(id=id)
        if ad.author != user:
            return Response({'error': 'You must be author'}, status=status.HTTP_401_UNAUTHORIZED)
        ad.delete()
        return Response({'message': 'Ad deleted successfully!'})
    except Ad.DoesNotExist:
        return Response({'error': 'Ad not found!'}, status=404)


@swagger_auto_schema(method='post', manual_parameters=[
    openapi.Parameter('id', openapi.IN_QUERY, description='ID of the Ad', type=openapi.TYPE_INTEGER),
    openapi.Parameter('comment', openapi.IN_QUERY, description='Response comment to Ad', type=openapi.TYPE_STRING),
])
@api_view(['POST'])
def response_ad(request):
    user = check_token(request)
    if not user:
        return Response('Non authorized', status=status.HTTP_401_UNAUTHORIZED)

    id = request.query_params.get('id')
    comment = request.query_params.get('comment')
    try:
        ad = Ad.objects.get(id=id)
        ad_response = AdResponse.objects.create(
            ad=ad,
            responder=user,
            response_comment=comment
        )
        ad_response.save()
        return Response({'message': 'Response sent!'})
    except Ad.DoesNotExist:
        return Response({'error': 'Ad not found!'}, status=404)


@swagger_auto_schema(method='get', manual_parameters=[
    openapi.Parameter('id', openapi.IN_QUERY, description='ID of the Ad', type=openapi.TYPE_INTEGER),
])
@api_view(['get'])
def get_responses(request):
    responses = []
    user = check_token(request)
    if not user:
        return Response('Non authorized', status=status.HTTP_401_UNAUTHORIZED)

    id = request.query_params.get('id')
    try:
        ad = Ad.objects.get(id=id)
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


@swagger_auto_schema(method='post', manual_parameters=[
    openapi.Parameter('ad_id', openapi.IN_QUERY, description='id of ad', type=openapi.TYPE_INTEGER),
    openapi.Parameter('response_id', openapi.IN_QUERY, description='id of response', type=openapi.TYPE_STRING),
])
@api_view(['post'])
def set_executor(request):
    user = check_token(request)
    if not user:
        return Response('Non authorized', status=status.HTTP_401_UNAUTHORIZED)

    ad_id = request.query_params.get('ad_id')
    response_id = request.query_params.get('response_id')
    try:
        ad = Ad.objects.get(id=ad_id)
        response = AdResponse.objects.get(id=response_id)
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




@swagger_auto_schema(method='put', manual_parameters=[
    openapi.Parameter('id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='ID of the AD', required=True),
    openapi.Parameter('title', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Title of the Ad'),
    openapi.Parameter('description', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Description of the Ad'),
    openapi.Parameter('category', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Category of the Ad'),
    openapi.Parameter('budget', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Budget of the Ad'),
    openapi.Parameter('contact_info', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                      description='Contact information for the Ad'),
    openapi.Parameter('files', openapi.IN_QUERY, type=openapi.TYPE_FILE, description='Files of the Ad'),
])
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


class AdList(generics.ListCreateAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
