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

import redis # type: ignore
session_storage = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)


client = Minio(endpoint="localhost:9000",   
               access_key='minio',          
               secret_key='minio124',       
               secure=False) 


@authentication_classes([BasicAuthentication, SessionAuthentication])
@swagger_auto_schema(method='POST', request_body=DocumentsSerializer)
@api_view(['Get', 'Post']) 
def get_documents(request, format=None):
    """
    Возвращает список активных документов 
    """
    if request.method == 'GET':
        print('get')
        query = request.GET.get("title")
        min_price = request.GET.get("minprice")
        max_price = request.GET.get("maxprice")
        
            
        if query:
            documents = Documents.objects.filter(
                Q(document_status = 'active'),
                Q(document_title__icontains = query.lower())
            ).order_by('document_title')
        else:
            documents = Documents.objects.filter(document_status = 'active').order_by('document_title')
            
        if min_price:
            if not min_price.isdigit():
                min_price = 0
            documents = documents.filter(Q(document_price__gte = min_price))
            
        if max_price:
            if not max_price.isdigit():
                min_price = 1000000
            documents = documents.filter(Q(document_price__lte = max_price))
        
        for doc in documents:
            if doc.document_image == 'not_found.jpg':
                url = client.get_presigned_url(
                    "GET",
                    "documents",
                    "not_found.jpg",
                )
                doc.document_image = url
                continue
            url = client.get_presigned_url(
                "GET",
                "documents",
                f"{doc.document_name}.jpg",
            )
            doc.document_image = url
        serializer = DocumentsSerializer(documents, many=True)
        return Response(serializer.data)
    
    if request.method == 'POST':
        try:
            ssid = request.COOKIES["session_id"]
        except:
            return Response({"error": "Нет доступа."}, status=403)
        user = CustomUser.objects.get(email=session_storage.get(ssid).decode('utf-8'))
        if not(user.is_staff or user.is_superuser):
            return Response({"error": "Нет доступа."}, status=403)
        print('post')
        serializer = DocumentsSerializer(data=request.data)
        if serializer.is_valid():
            try:
                if 'document_image' not in serializer.validated_data:
                    client.stat_object(bucket_name='documents',     
                    object_name=f"not_found.jpg")
                else:
                    client.stat_object(bucket_name='documents',     
                        object_name=f"{serializer.validated_data['document_name']}.jpg")
            except:
                client.fput_object(bucket_name='documents',  
                        object_name=f"{serializer.validated_data['document_name']}.jpg",  
                        file_path=serializer.validated_data['document_image'])
                
            if 'document_image' not in serializer.validated_data:
                serializer.validated_data['document_image'] = f"not_found.jpg"
            else:
                serializer.validated_data['document_image'] = f"{serializer.validated_data['document_name']}.jpg"
            serializer.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@permission_classes([IsManager])
@authentication_classes([BasicAuthentication, SessionAuthentication])
@swagger_auto_schema(method='PUT', request_body=DocumentsSerializer)
@api_view(['Get', 'Put', 'DELETE']) 
def get_document(request, pk, format=None):
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
                if document.document_image != request.data['document_image']:
                    client.remove_object("documents", f"{document.document_image}")
                    client.fput_object(bucket_name='documents',  
                                        object_name=f"{document.document_name}.jpg",  
                                        file_path=serializer.validated_data['document_image'])
                    serializer.validated_data['document_image'] = f"{document.document_name}.jpg"
            except:
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
@authentication_classes([SessionAuthentication])
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
            'documents': serializer_documents.data
        }       
        result.append(docs_apps_data)
    return Response(result)


@permission_classes([IsAuthenticated])
@authentication_classes([BasicAuthentication, SessionAuthentication])
@swagger_auto_schema(method='put', request_body=ApplicationsSerializer)
@api_view(['Get', 'Put', 'Delete']) 
def get_application(request, pk, format=None):
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
@authentication_classes([BasicAuthentication, SessionAuthentication])
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
@authentication_classes([BasicAuthentication, SessionAuthentication])  
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
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@authentication_classes([BasicAuthentication, SessionAuthentication])     
@api_view(["Delete"]) 
def delete_document_application(request, document_id, application_id, formate=None):
    try:
        ssid = request.COOKIES["session_id"]
    except:
        return Response(status=status.HTTP_403_FORBIDDEN)
    user = CustomUser.objects.get(email=session_storage.get(ssid).decode('utf-8'))
    if user.is_staff or user.is_superuser:
        return Response({"error": "Нет доступа"}, status=403)
    else:
        document_application = get_object_or_404(NameChangeApplications, document_id=document_id, application_id=application_id, client_id=user.id)
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

        response = HttpResponse("{'status': 'ok'}")
        response.set_cookie("session_id", random_key)

        return response
    
    else:
        return HttpResponse("{'status': 'error', 'error': 'login failed'}")
    

@permission_classes([AllowAny])
@authentication_classes([])
@csrf_exempt
@swagger_auto_schema(method='post')
@api_view(['Post'])
def logout_view(request):
    try:
        ssid = request.COOKIES["session_id"]
    except:
        return HttpResponse("{'status': 'error', 'error': 'logout failed'}")
    print(ssid)
    session_storage.delete(ssid)
    logout(request._request)
    response = HttpResponse("{'status': 'success'}")
    response.delete_cookie("session_id")
    return response

