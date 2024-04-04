from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from .serializers import AdSerializer, AdFileSerializer
from rest_framework import generics, status
from .models import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from pytils.translit import slugify
from django.utils import timezone


def all_ads(request):
    ads = []
    for ad in Ad.objects.all():
        ads.append({'ad': ad})

    context = {
        'ads': ads,
    }
    return render(request, 'all_ads.html', context)

def ad_data(ad: Ad) -> dict:
    executor_name = ad.executor.slug if ad.executor else 'None'
    response_count = AdResponse.objects.filter(ad=ad).count()

    files_query = [({'name': file.file.name, 'file_id': file.id}) for file in ad.files.all()] if ad.files.exists() else ['None']

    return {
        'author': ad.author.slug,
        'author firstname': ad.author.first_name,
        'author lastname': ad.author.last_name,
        'executor': executor_name,
        'response_count': response_count,
        'title': ad.title,
        'id': ad.id,
        'slug': ad.slug,
        'description': ad.description,
        'category': ad.category,
        'type': ad.type,
        'budget': ad.budget,
        'pub_date': ad.pub_date,
        'close_date': ad.closed_date,
        'contact_info': ad.contact_info,
        'status': ad.status,
        'files': files_query,
    }

@swagger_auto_schema(method='get', manual_parameters=[
        openapi.Parameter('id', openapi.IN_QUERY, description='id', type=openapi.TYPE_INTEGER, required=True),
])
@api_view(['GET'])
def api_ad_view(request):
    id = request.query_params.get('id')
    ad = get_object_or_404(Ad, id=id)
    return Response({'ad': ad_data(ad)}, status=status.HTTP_201_CREATED)
@swagger_auto_schema(method='get')
@api_view(['GET'])
def get_ads(request):
    profiles = []

    for ad in Ad.objects.all():
        profiles.append(ad_data(ad))

    return Response({'ads': profiles}, status=status.HTTP_201_CREATED)



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
    openapi.Parameter('title', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Title of the Ad', required=True),
    openapi.Parameter('description', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Description of the Ad', required=True),
    openapi.Parameter('category', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Category of the Ad', required=True),
    openapi.Parameter('type', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Type of the Ad', required=True, enum=[
        'контрольная работа', 'курсовая работа', 'дипломная работа', 'задача', 'лабораторная работа', 'тест', 'эссе',
        'практика', 'чертеж', 'перевод', 'диссертация', 'бизнез-план', 'билеты', 'статья', 'доклад', 'шпаргалка', 'творческая работа'
    ]),
    openapi.Parameter('budget', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Budget of the Ad', required=True),
    openapi.Parameter('contact_info', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Contact information for the Ad', required=True),
    openapi.Parameter('files', in_=openapi.IN_FORM, type=openapi.TYPE_FILE, description='Files to upload with the Ad'),
])
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def create_ad(request):
    author = request.user
    if not author:
        return Response('Non authorized', status=status.HTTP_401_UNAUTHORIZED)

    try:
        title = request.query_params.get('title')
        description = request.query_params.get('description')
        budget = request.query_params.get('budget')
        category = request.query_params.get('category')
        type = request.query_params.get('type')
        contact_info = request.query_params.get('contact_info')
        files = request.FILES.getlist('files')
    except:
        title = request.data.get('title')
        description = request.data.get('description')
        budget = request.data.get('budget')
        category = request.data.get('category')
        type = request.data.get('type')
        contact_info = request.data.get('contact_info')
        files = request.FILES.getlist('files')

    ad = Ad.objects.create(
        author=author,
        title=title,
        slug=slugify(title),
        description=description,
        category=category,
        type=type,
        budget=budget,
        contact_info=contact_info,
    )

    for file in files:
        file_object = AdFile.objects.create(file=file)
        ad.files.add(file_object)

    return Response({'message': 'Ad created successfully'})


@swagger_auto_schema(method='post', manual_parameters=[
    openapi.Parameter('ad_id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='ID of the Ad', required=True),
    openapi.Parameter('file', in_=openapi.IN_FORM, type=openapi.TYPE_FILE, description='File to upload', required=True),
])
@api_view(['POST'])
@parser_classes([MultiPartParser])
def add_file_to_ad(request):
    user = request.user
    if not user:
        return Response('Non authorized', status=status.HTTP_401_UNAUTHORIZED)

    ad_id = request.query_params.get('ad_id')
    file = request.FILES.get('file')

    ad = get_object_or_404(Ad, id=ad_id)
    if ad.author != user and not request.user.is_superuser:
        return Response({'error': 'You must be author'}, status=status.HTTP_401_UNAUTHORIZED)

    file_object = AdFile.objects.create(file=file)
    ad.files.add(file_object)

    return Response({'message': 'File added successfully'})


@swagger_auto_schema(method='get', manual_parameters=[
    openapi.Parameter('ad_id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='ID of the Ad', required=True),
])
@api_view(['GET'])
def list_files_for_ad(request):
    ad_id = request.query_params.get('ad_id')

    if not ad_id:
        return Response({'error': 'Ad ID is required'}, status=400)

    ad = get_object_or_404(Ad, id=ad_id)
    files = ad.files.all()

    files_info = [{'id': file.id, 'name': file.file.name} for file in files]

    return Response({'files': files_info})


@swagger_auto_schema(method='delete', manual_parameters=[
    openapi.Parameter('ad_id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='ID of the Ad', required=True),
    openapi.Parameter('file_id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='ID of the File to delete', required=True),
])
@api_view(['DELETE'])
def delete_file_from_ad(request):
    user = request.user
    if not user:
        return Response('Non authorized', status=status.HTTP_401_UNAUTHORIZED)
    ad_id = request.query_params.get('ad_id')
    file_id = request.query_params.get('file_id')

    if not ad_id or not file_id:
        return Response({'error': 'Ad ID and File ID are required'}, status=400)

    ad = get_object_or_404(Ad, id=ad_id)
    if ad.author != user and not request.user.is_superuser:
        return Response({'error': 'You must be author'}, status=status.HTTP_401_UNAUTHORIZED)

    file_object = get_object_or_404(AdFile, id=file_id)
    ad.files.remove(file_object)

    return Response({'message': 'File removed successfully'})


@swagger_auto_schema(method='get')
@api_view(['GET'])
def my_ads(request):
    profiles = []
    user = request.user
    if not user:
        return Response({'error': 'Unauthorized'}, status=401)

    ads = Ad.objects.filter(author=user)
    for ad in ads:
        profiles.append(ad_data(ad))

    return Response({'ads': profiles}, status=status.HTTP_201_CREATED)


@swagger_auto_schema(method='get')
@api_view(['GET'])
def my_closed_ads(request):
    profiles = []
    user = request.user
    if not user:
        return Response({'error': 'Unauthorized'}, status=401)

    ads = Ad.objects.filter(executor=user, status='closed')
    for ad in ads:
        profiles.append(ad_data(ad))
    return Response({'ads': profiles}, status=status.HTTP_201_CREATED)


@swagger_auto_schema(method='get')
@api_view(['GET'])
def ads_im_completing(request):
    profiles = []
    user = request.user
    if not user:
        return Response({'error': 'Unauthorized'}, status=401)

    ads = Ad.objects.filter(executor=user)
    for ad in ads:
        profiles.append(ad_data(ad))
    return Response({'ads': profiles}, status=status.HTTP_201_CREATED)


@swagger_auto_schema(method='post', manual_parameters=[
    openapi.Parameter('ad_id', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='ID of the Ad', required=True),
    openapi.Parameter('reason', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Reason of close the ad', required=False),
])
@api_view(['POST'])
def close_ad(request):
    user = request.user
    if not user:
        return Response('Non authorized', status=status.HTTP_401_UNAUTHORIZED)
    ad_id = request.query_params.get('ad_id')
    # Пока хз где использовать
    reason = request.query_params.get('reason')

    if not ad_id:
        return Response({'error': 'Ad ID is required'}, status=400)

    ad = get_object_or_404(Ad, id=ad_id)
    if ad.author != user and not request.user.is_superuser:
        return Response({'error': 'You must be author'}, status=status.HTTP_401_UNAUTHORIZED)

    ad.status = Ad.CLOSED
    ad.closed_date = timezone.now()
    ad.save()


@swagger_auto_schema(method='delete', manual_parameters=[
    openapi.Parameter('id', openapi.IN_QUERY, description='ID of the Ad', type=openapi.TYPE_INTEGER)])
@api_view(['DELETE'])
def delete_ad(request):
    user = request.user
    if not user:
        return Response('Non authorized', status=status.HTTP_401_UNAUTHORIZED)

    id = request.query_params.get('id')
    try:
        ad = Ad.objects.get(id=id)
        if ad.author != user and not request.user.is_superuser:
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
    user = request.user
    if not user:
        return Response('Non authorized', status=status.HTTP_401_UNAUTHORIZED)

    id = request.query_params.get('id')
    comment = request.query_params.get('comment')
    try:
        ad = Ad.objects.get(id=id)
        if ad.status != Ad.OPEN:
            return Response({'error': 'This AD is not open'}, status=status.HTTP_400_BAD_REQUEST)
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
    user = request.user
    if not user:
        return Response('Non authorized', status=status.HTTP_401_UNAUTHORIZED)

    id = request.query_params.get('id')
    try:
        ad = Ad.objects.get(id=id)
        if ad.author != user and not request.user.is_superuser:
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
    user = request.user
    if not user:
        return Response('Non authorized', status=status.HTTP_401_UNAUTHORIZED)

    ad_id = request.query_params.get('ad_id')
    response_id = request.query_params.get('response_id')
    try:
        ad = Ad.objects.get(id=ad_id)
        response = AdResponse.objects.get(id=response_id)
        if ad.author != user and not request.user.is_superuser:
            return Response({'error': 'You must be author'}, status=status.HTTP_401_UNAUTHORIZED)
        if response.ad == ad:
            ad.executor = response.responder
            ad.status = Ad.IN_PROGRESS
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
    openapi.Parameter('type', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Type of the Ad'),
    openapi.Parameter('budget', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Budget of the Ad'),
    openapi.Parameter('contact_info', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Contact information for the Ad'),
])
@api_view(['PUT'])
def edit_ad(request):
    user = request.user
    if not user:
        return Response('Non authorized', status=status.HTTP_401_UNAUTHORIZED)

    ad_id = request.query_params.get('id')
    try:
        ad = Ad.objects.get(id=ad_id)
        if ad.author != user and not request.user.is_superuser:
            return Response({'error': 'You must be author'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            title = request.query_params.get('title', ad.title)
            description = request.query_params.get('description', ad.description)
            category = request.query_params.get('category', ad.category)
            type = request.query_params.get('type', ad.type)
            budget = request.query_params.get('budget', ad.budget)
            contact_info = request.query_params.get('contact_info', ad.contact_info)
        except:
            title = request.data.get('title', ad.title)
            description = request.data.get('description', ad.description)
            category = request.data.get('category', ad.category)
            type = request.data.get('type', ad.type)
            budget = request.data.get('budget', ad.budget)
            contact_info = request.data.get('contact_info', ad.contact_info)

        ad.author = user
        ad.title = title
        ad.slug = slugify(title)
        ad.description = description
        ad.category = category
        ad.type = type
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
