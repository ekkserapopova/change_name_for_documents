from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from .permitions import IsAdmin, IsManager
from .serializers import DocumentsSerializer, ApplicationsSerializer, DocumentsApplicationsSerializer, UserSerializer
from .models import CustomUser, Documents, NameChangeApplications, DocumentsApplications
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from datetime import datetime
from minio import Minio
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from django.views.decorators.csrf import csrf_protect, csrf_exempt
import uuid
from change_surname.settings import REDIS_HOST, REDIS_PORT
from drf_yasg import openapi
import requests 
import os

import redis # type: ignore
session_storage = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)


client = Minio(endpoint="127.0.0.1:9000",   
               access_key='minio',          
               secret_key='minio124',       
               secure=False) 



dict = {'ё': 'yo', 'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ж': 'zh',
     'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p',
     'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch', 'ш': 'sh',
     'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'}


# @authentication_classes([BasicAuthentication, SessionAuthentication])
@swagger_auto_schema(
    methods=['GET'],
    manual_parameters=[
        openapi.Parameter('title', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Document title'),
        openapi.Parameter('minprice', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Minimum price'),
        openapi.Parameter('maxprice', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Maximum price'),
    ],
    responses={
        200: openapi.Response(
            description="Documents",
            schema=DocumentsSerializer(many=True),
        ),
    },
)
@swagger_auto_schema(
    methods=['POST'],
    request_body=DocumentsSerializer
)
@api_view(['Get', 'Post']) 
def documents(request, format=None):
    """
    Возвращает список активных документов 
    """
    if request.method == 'GET':
        try:
            ssid = request.COOKIES["session_id"]
            
        except:
            ssid = None
            
        query = request.GET.get("title")
        min_price = request.GET.get("minprice")
        max_price = request.GET.get("maxprice")
        doc_status = request.GET.get('status')
        
        if ssid is not None:
            user_id = CustomUser.objects.get(email=session_storage.get(ssid).decode('utf-8')).id
        else:
            # print(1)
            user_id = None
            
        if user_id:
            try:
                draft = NameChangeApplications.objects.filter(application_status='created', client_id=user_id)
                print(draft[0].application_id)
            except:
                draft = None
        else:
            draft = None
            
        if doc_status:
            documents = Documents.objects.filter(document_status = doc_status).order_by('document_title')
        else:
            documents = Documents.objects.filter(document_status = 'active').order_by('document_title')
        
        if query:
            documents = documents.filter(
                Q(document_title__icontains = query.lower())
            )
            
        # if status:
        #     documents = documents.filter(document_status = status)
        # else:
        #     documents = documents.filter(document_status = 'active')
            
        if min_price:
            if not min_price.isdigit():
                min_price = 0
            documents = documents.filter(Q(document_price__gte = min_price))
            
        if max_price:
            if not max_price.isdigit():
                min_price = 1000000
            documents = documents.filter(Q(document_price__lte = max_price))
        # print(documents)
        for doc in documents:
            
            if doc.document_image == 'not_found.jpg':
                url = client.get_presigned_url(
                    "GET",
                    "documents",
                    "not_found.jpg",
                )
                doc.document_image = url
                continue
            else:
                
                url = client.get_presigned_url(
                    "GET",
                    "documents",
                    doc.document_image,
                )
                print(url)
            # print(1)
            doc.document_image = url
            
        serializer = DocumentsSerializer(documents, many=True)
        if draft:
            docs = {
                'documents': serializer.data,
                'draft_id': draft[0].application_id
            }     
        else:
            docs = {
                'documents': serializer.data,
                'draft_id': -1
            }  
        # print(docs)
        return Response(docs)
    
    if request.method == 'POST':
        try:
            ssid = request.COOKIES["session_id"]
        except:
            return Response({"error": "Нет доступа."}, status=403)
        
        dict = {'ё': 'yo', 'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ж': 'zh',
            'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p',
            'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch', 'ш': 'sh',
            'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'}
        user = CustomUser.objects.get(email=session_storage.get(ssid).decode('utf-8'))
        if not(user.is_staff or user.is_superuser):
            return Response({"error": "Нет доступа."}, status=403)
        print('post')
        serializer = DocumentsSerializer(data=request.data)
        if serializer.is_valid():
            try:
                
                s = list(map(lambda x: dict.get(x, '-'), serializer.validated_data['document_title']))
                name = ''.join(s)
                serializer.validated_data['document_name'] = name
                # serializer.validated_data['document_image'] = f"not_found.jpeg"
                if 'document_image' not in serializer.validated_data:
                    client.stat_object(bucket_name='documents',     
                    object_name=f"not_found.jpg")
                else:
                    client.stat_object(bucket_name='documents',     
                        object_name=f"{serializer.validated_data['document_image']}")
            except:
                if 'document_image' in serializer.validated_data:
                    file_path = os.path.join("/Users/ekksera/Desktop/rip_pictures",
                                             serializer.validated_data['document_image'])
                    print('add')
                    client.fput_object(bucket_name='documents',
                                       object_name=f"{serializer.validated_data['document_image']}",
                                       file_path=file_path)
                    print('add')
                
            if 'document_image' not in serializer.validated_data:
                serializer.validated_data['document_image'] = f"not_found.jpg"
            else:
                serializer.validated_data['document_image'] = f"{serializer.validated_data['document_image']}"
            serializer.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@permission_classes([IsManager])
# @authentication_classes([BasicAuthentication, SessionAuthentication])
@swagger_auto_schema(method='PUT', request_body=DocumentsSerializer)
@api_view(['Get', 'Put', 'DELETE']) 
def document(request, pk, format=None):
    if request.method == 'GET':
        document = get_object_or_404(Documents, pk=pk)
        print(document.document_image)
        if request.method == 'GET':
            """
            Возвращает информацию об одном документе
            """
            if document.document_image == 'not_found.jpg':
                url = client.get_presigned_url(
                    "GET",
                    "documents",
                    "not_found.jpg",
                )
            else:
                url = client.get_presigned_url(
                "GET",
                "documents",
                f"{document.document_name}.jpg",
                )
            document.document_image = url
            serializer = DocumentsSerializer(document)
            print(document.document_image)
            return Response(serializer.data)
    elif request.method == 'PUT':
        """
        Обновляет информацию о документе
        """
        try:
            ssid = request.COOKIES["session_id"]
        except:
            return Response({"error": "Нет доступа."}, status=403)
        user = CustomUser.objects.get(email=session_storage.get(ssid).decode('utf-8'))
        if not(user.is_staff or user.is_superuser):
            return Response({"error": "Нет доступа."}, status=403)
        print('put')
        document = get_object_or_404(Documents, pk=pk)
        serializer = DocumentsSerializer(document, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                if request.data['document_image'] != document.document_image:
                    # client.remove_object("documents", f"{document.document_image}")
                    print(1)
                    file_path = os.path.join("/Users/ekksera/Desktop/rip_pictures",
                                            request.data['document_image'])
                    client.fput_object(bucket_name='documents',  
                                            object_name=f"{request.data['document_image']}",  
                                            file_path=file_path)
                    serializer.validated_data['document_image'] = f"{request.data['document_image']}"
                serializer.save()
            except:
                serializer.validated_data['document_image'] = document.document_image
                serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    elif request.method == 'DELETE':
        """
        Удаляет информацию о документе - устанавливает статус 'deleted'
        """
        print('ok')
        try:
            ssid = request.COOKIES["session_id"]
            print('ok')
        except:
            print('ok')
            return Response({"error": "Нет доступа."}, status=403)
        print('ok')
        user = CustomUser.objects.get(email=session_storage.get(ssid).decode('utf-8'))
        if not (user.is_staff or user.is_superuser):
            return Response({"error": "Нет доступа."}, status=403)
            
        document = get_object_or_404(Documents, pk=pk)
        document.document_status = 'deleted'
        document.save()
        serializer =  DocumentsSerializer(document)
        print('ok')
        return Response(serializer.data)


@csrf_protect
@permission_classes([IsAuthenticated])
@authentication_classes([BasicAuthentication, SessionAuthentication])
@swagger_auto_schema(method='post', request_body=ApplicationsSerializer)
@api_view(['Post']) 
def post_application(request, pk, format=None):
    """
    Добавляет новую заявку
    """
    try:
        ssid = request.COOKIES["session_id"]
    except:
        try: 
            ssid = request.data["session_id"]
        except:
            return Response(status=status.HTTP_403_FORBIDDEN)
    user = CustomUser.objects.get(email=session_storage.get(ssid).decode('utf-8')).id
    print(user)
    document = get_object_or_404(Documents, pk=pk)
    request.data['client_id'] = user
    request.data['moderator_id'] = 1
    serializer_app = ApplicationsSerializer(data=request.data)
    try:
        application = NameChangeApplications.objects.get(
            application_status = 'created',
            client_id_id = user
        )
        serializer_doc_app = DocumentsApplicationsSerializer(data={'document_id': pk, 'application_id': application.application_id})
    except Exception as e:
        print(e)
        serializer_app.client_id = user
        if serializer_app.is_valid():
            new_application = serializer_app.save()
            serializer_doc_app = DocumentsApplicationsSerializer(data={'document_id': pk, 'application_id': new_application.application_id})
        else:
            return Response(serializer_app.errors, status=status.HTTP_400_BAD_REQUEST)
    if serializer_doc_app.is_valid():
        serializer_doc_app.save()
    else:
        return Response(serializer_doc_app.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer_doc_app.data)



@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    method='GET',
    manual_parameters=[
        openapi.Parameter('status', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Status'),
        openapi.Parameter('startdate', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='From'),
        openapi.Parameter('enddate', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='To'),
    ],
)
@csrf_exempt
@api_view(['Get']) 
def get_applications(request, format=None):
    """
    Возвращает список заявок
    """
    try:
        ssid = request.COOKIES["session_id"]
    except:
        return Response({"error": "Нет доступа."}, status=403)
    
    user = CustomUser.objects.get(email=session_storage.get(ssid).decode('utf-8'))

    startdate = request.GET.get("startdate")
    enddate = request.GET.get("enddate")
    statuses = request.GET.get("status")
    
    if user.is_staff or user.is_superuser:
        applications = NameChangeApplications.objects.all()
    else:
        applications = NameChangeApplications.objects.filter(client_id=user.id)
    
    if startdate:
        applications = applications.filter(
            Q(date_of_application_acceptance__gte=startdate)
        )
        
    if enddate:
        applications = applications.filter(
            Q(date_of_application_acceptance__lte=enddate)
        )
        
    if statuses:
        statuses=statuses.split(",")
        filters = Q()
        for status in statuses:
            filters |= Q(application_status=status)
        applications = applications.filter(
            filters
        )
    result = []
    for application in applications:
        serializer = ApplicationsSerializer(application)
        # client = CustomUser.objects.get(id=application.client_id)
        # print(application.client_id.email)
        docs_apps = DocumentsApplications.objects.filter(application_id=application.application_id)
        docs_apps_serializer = DocumentsApplicationsSerializer(docs_apps, many=True)
        filters = Q()
        for doc_app in docs_apps:
            filters |= Q(document_id=doc_app.document_id_id)
        if filters == Q():
            documents = {}
        else:
            documents = Documents.objects.filter(filters)
        serializer_documents = DocumentsSerializer(documents, many=True)
        docs_apps_data = {
            'application': serializer.data,
            "client_email": application.client_id.email,
            'documents': serializer_documents.data
        }       
        result.append(docs_apps_data)
    return Response(result)


@permission_classes([IsAuthenticated])
# @authentication_classes([BasicAuthentication, SessionAuthentication])
@swagger_auto_schema(method='put', request_body=ApplicationsSerializer)
@api_view(['Get', 'Put', 'Delete']) 
def application(request, pk, format=None):
    """
    Возвращает информацию об одной заявке
    """
    if request.method == 'GET':
        try:
            ssid = request.COOKIES["session_id"]
        except:
            return Response({"error": "Нет доступа."}, status=403)
        user = CustomUser.objects.get(email=session_storage.get(ssid).decode('utf-8'))
        if user.is_staff or user.is_superuser:
            application = get_object_or_404(NameChangeApplications, pk=pk)
        else:
            application = get_object_or_404(NameChangeApplications, pk=pk, client_id=user.id)
        
        serializer = ApplicationsSerializer(application)
        docs_apps = DocumentsApplications.objects.filter(application_id=pk)
        serializer_docs_apps = DocumentsApplicationsSerializer(docs_apps, many=True)
        filters = Q()
        for doc_app in docs_apps:
            filters |= Q(document_id=doc_app.document_id_id)
        print(filters)
        if filters != Q():
            documents = Documents.objects.filter(filters)
        else:
            documents = {}
        serializer_documents = DocumentsSerializer(documents, many=True)
        
        docs_apps_data = {
            'application': serializer.data,
            "client_email": application.client_id.email,
            'documents': serializer_documents.data
        }
            
        return Response(docs_apps_data)
    elif request.method == 'PUT':
        try:
            ssid = request.COOKIES["session_id"]
        except:
            return Response({"error": "Нет доступа."}, status=403)
        user = CustomUser.objects.get(email=session_storage.get(ssid).decode('utf-8'))
        if user.is_staff:
            return Response({"error": "Нет доступа."}, status=403)
        else:
            application = get_object_or_404(NameChangeApplications, pk=pk, client_id=user.id)
        # application = get_object_or_404(NameChangeApplications, pk=pk)
        serializer = ApplicationsSerializer(application, data=request.data, partial=True)
        if application.application_status != 'created':
            return Response({"error": "Неверный статус."}, status=400)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        try:
            ssid = request.COOKIES["session_id"]
        except:
            return Response(status=status.HTTP_403_FORBIDDEN)
        user = CustomUser.objects.get(email=session_storage.get(ssid).decode('utf-8'))
        if user.is_staff or user.is_superuser:
            return Response({"error": "Нет доступа"}, status=403)
        else:
            application = get_object_or_404(NameChangeApplications, pk=pk, client_id=user.id)
        # application = get_object_or_404(NameChangeApplications, pk=pk)
        if application.application_status != 'created':
            return Response({"error": "Неверный статус."}, status=400)       
        application.application_status = 'deleted'
        application.date_of_application_completion = datetime.now()
        application.save()
        serializer = ApplicationsSerializer(application) 
        return Response(serializer.data)

   
@permission_classes([IsManager])
# @authentication_classes([BasicAuthentication, SessionAuthentication])
@swagger_auto_schema(method='put', request_body=ApplicationsSerializer)
@api_view(['PUT']) 
def put_applications_moderator(request, pk, format=None):
    """
    Обновляет информацию о документе модератор
    """
    try:
        ssid = request.COOKIES["session_id"]
    except:
        return Response({"error": "Нет доступа."}, status=403)
    user = CustomUser.objects.get(email=session_storage.get(ssid).decode('utf-8'))
    if not(user.is_staff or user.is_superuser):
        return Response({"error": "Нет доступа."}, status=403)
    application = get_object_or_404(NameChangeApplications, pk=pk)
    print(application.application_status)
    if request.data['application_status'] not in ['completed', 'canceled'] or application.application_status != 'in_progress':
        return Response({"error": "Неверный статус."}, status=400)
    application.application_status = request.data['application_status']
    application.date_of_application_completion = datetime.now()
    serializer = ApplicationsSerializer(application, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([IsAuthenticated])
# @authentication_classes([BasicAuthentication, SessionAuthentication])  
@swagger_auto_schema(method='put', request_body=ApplicationsSerializer)
@api_view(['PUT']) 
def put_applications_client(request, pk, format=None):
    """
    Обновляет информацию о документе клиент
    """
    try:
        ssid = request.COOKIES["session_id"]
    except:
        return Response(status=status.HTTP_403_FORBIDDEN) 
    user = CustomUser.objects.get(email=session_storage.get(ssid).decode('utf-8'))
    if user.is_staff or user.is_superuser:
        return Response({"error": "Нет доступа"}, status=403)
    else:
        application = get_object_or_404(NameChangeApplications, pk=pk, client_id=user.id)
    # application = get_object_or_404(NameChangeApplications, pk=pk)
    if request.data['application_status'] != 'in_progress' or application.application_status != 'created':
        return Response({"error": "Неверный статус."}, status=400)
    application.application_status = request.data['application_status']
    application.date_of_application_acceptance = datetime.now()
    serializer = ApplicationsSerializer(application, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        other_service_url = 'http://localhost:8080/name'
        other_service_data = {'application_id': application.application_id}
        other_service_response = requests.post(other_service_url, json=other_service_data)

        # Проверить успешность запроса к другому сервису
        if other_service_response.status_code == 200:
            return Response(serializer.data)
        else:
            return Response({"error": "Не удалось обновить в другом сервисе"}, status=500)

        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@csrf_exempt
@permission_classes([IsAuthenticated])
@authentication_classes([BasicAuthentication, SessionAuthentication])
@api_view(['Delete']) 
def delete_document_application(request, document_id, application_id, formate=None):
    try:
        ssid = request.COOKIES["session_id"]
    except:
        return Response(status=status.HTTP_403_FORBIDDEN)
    user = CustomUser.objects.get(email=session_storage.get(ssid).decode('utf-8'))
    if user.is_staff or user.is_superuser:
        return Response({"error": "Нет доступа"}, status=403)
    else:
        document_application = get_object_or_404(DocumentsApplications, document_id=document_id, application_id=application_id)
    # document_application = get_object_or_404(DocumentsApplications, document_id=document_id, application_id=application_id)
    document_application.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
   
class UserViewSet(viewsets.ModelViewSet):
    """Класс, описывающий методы работы с пользователями
    Осуществляет связь с таблицей пользователей в базе данных
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    model_class = CustomUser

    def create(self, request):
        """
        Функция регистрации новых пользователей
        Если пользователя c указанным в request email ещё нет, в БД будет добавлен новый пользователь.
        """
        if self.model_class.objects.filter(email=request.data['email']).exists():
            return Response({'status': 'Exist'}, status=400)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            print(serializer.data)
            self.model_class.objects.create_user(email=serializer.data['email'],
                                     password=serializer.data['password'],
                                     first_name=serializer.data['first_name'],
                                     last_name=serializer.data['last_name'],
                                     otchestvo=serializer.data['otchestvo'],
                                     pasport=serializer.data['pasport'],
                                     is_superuser=serializer.data['is_superuser'],
                                     is_staff=serializer.data['is_staff'])
            return Response({'status': 'Success'}, status=200)
        return Response({'status': 'Error', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    
    
@permission_classes([AllowAny])
@authentication_classes([])
@swagger_auto_schema(method='post', request_body=UserSerializer)
@csrf_exempt
@api_view(['POST'])
def login_view(request):
    email = request.data["email"] # допустим передали username и password
    password = request.data["password"]
    user = authenticate(request, username=email, password=password)
    print(user)
    if user is not None:
        random_key = str(uuid.uuid4())
        session_storage.set(random_key, email)
        data = {
            'id': user.id,
            'is_moderator': user.is_staff,
            'session_id': random_key
        }
        response = Response(data, status=status.HTTP_201_CREATED)
        # response.set_cookie("session_id", random_key)
        response.set_cookie("session_id", random_key, samesite='None', secure=True)
        # response.delete_cookie('sessionid')
        return response
    
    else:
        return JsonResponse({'status': 'Error', 'message': 'Login failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@permission_classes([AllowAny])
@authentication_classes([])
@csrf_exempt
@swagger_auto_schema(method='post')
@api_view(['Post'])
def logout_view(request):
    # session_storage.flushdb()
    session_storage.delete("fa513344-fcc6-41f6-ba8c-236d51201579")
    print("1")
    try:
        ssid = request.COOKIES["session_id"]
    except Exception as e:
        try: 
            ssid = request.data["session_id"]
        except:
            print(request.COOKIES)
            return HttpResponse("{'status': 'error', 'error': 'logout failed'}")
    print(ssid)
    session_storage.delete(ssid)
    logout(request._request)
    response = HttpResponse("{'status': 'success'}")
    response.delete_cookie("session_id")
    return response

@permission_classes([AllowAny])
@authentication_classes([])
@swagger_auto_schema(method='post', request_body=UserSerializer)
@csrf_exempt
@api_view(['POST'])
def get_user(request):
    print(0)
    try:
        ssid = request.COOKIES["session_id"]
    except Exception as e:
        try: 
            ssid = request.data["session_id"]
            print(000)
        except:
            print(request.COOKIES)
            return HttpResponse("{'status': 'error', 'error': 'logout failed'}")
    if session_storage.exists(ssid):
        user = CustomUser.objects.get(email=session_storage.get(ssid).decode('utf-8'))
        data = {
                'id': user.id,
                'is_moderator': user.is_staff,
                'email' : user.email,
            }
        return Response(data, status=status.HTTP_200_OK)
    else:
        return Response({'status': 'Error', 'message': 'Session does not exist'})

#for async
PASSWORD = 'documents_for_change'

@api_view(["PUT"])
def update_mfc(request, pk):
    mfc_status = request.data['mfc_status']
    if mfc_status not in ("Отправлена","Не отправлена"):
        return Response({"error": "Неверное значение статуса МФЦ"}, status=400)
    password = request.data["password"]
    if password != PASSWORD:
        return Response(status=status.HTTP_403_FORBIDDEN)
    try:
        app = NameChangeApplications.objects.get(pk=pk)
        app.mfc_status = mfc_status
        app.save()
        return Response(status=status.HTTP_200_OK)
    except app.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)