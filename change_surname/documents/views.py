from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from .serializers import DocumentsSerializer, ApplicationsSerializer, DocumentsApplicationsSerializer
from .models import Documents, NameChangeApplications, DocumentsApplications
from rest_framework.decorators import api_view
from datetime import datetime
from minio import Minio
from django.conf import settings
from minio.commonconfig import REPLACE, CopySource


client = Minio(endpoint="localhost:9000",   # адрес сервера
               access_key='minio',          # логин админа
               secret_key='minio124',       # пароль админа
               secure=False)  


@api_view(['Get']) 
def get_active_documents(request, format=None):
    """
    Возвращает список активных документов 
    """
    print('get')
    documents = Documents.objects.filter(document_status = 'active').order_by('document_title')
    for doc in documents:
        url = client.get_presigned_url(
            "GET",
            "documents",
            f"{doc.document_name}.jpg",
        )
        doc.document_image = url
    serializer = DocumentsSerializer(documents, many=True)
    return Response(serializer.data)

@api_view(['Get']) 
def get_document(request, pk, format=None):
    document = get_object_or_404(Documents, pk=pk)
    print(document.document_image)
    if request.method == 'GET':
        """
        Возвращает информацию об одном документе
        """
        url = client.get_presigned_url(
            "GET",
            "documents",
            f"{document.document_name}.jpg",
        )
        document.document_image = url
        serializer = DocumentsSerializer(document)
        print(document.document_image)
        return Response(serializer.data)

@api_view(['Post']) 
def post_document(request, format=None):    
    """
    Добавляет новый документ
    """
    print('post')
    serializer = DocumentsSerializer(data=request.data)
    if serializer.is_valid():
        try:
            client.stat_object(bucket_name='documents',     
                object_name=f"{serializer.validated_data['document_name']}.jpg")
        except:
            client.fput_object(bucket_name='documents',  
                    object_name=f"{serializer.validated_data['document_name']}.jpg",  
                    file_path=serializer.validated_data['document_image'])
        serializer.validated_data['document_image'] = f"{serializer.validated_data['document_name']}.jpg"
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT']) 
def put_document(request, pk, format=None):
    """
    Обновляет информацию о документе
    """
    print('put')
    document = get_object_or_404(Documents, pk=pk)
    serializer = DocumentsSerializer(document, data=request.data)
    if serializer.is_valid():
        if document.document_image != request.data['document_image']:
            client.remove_object("documents", f"{document.document_image}")
            client.fput_object(bucket_name='documents',  
                                object_name=f"{serializer.validated_data['document_name']}.jpg",  
                                file_path=serializer.validated_data['document_image'])
            serializer.validated_data['document_image'] = f"{serializer.validated_data['document_name']}.jpg"
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['Post']) 
def post_application(request, pk, format=None):
    """
    Добавляет новую заявку
    """
    print('post')
    document = get_object_or_404(Documents, pk=pk)
    serializer_app = ApplicationsSerializer(data=request.data)
    try:
        application = NameChangeApplications.objects.get(
            application_status = 'created',
            client_id_id = request.data['client_id']
        )
        print('not create', application.application_id)
        serializer_doc_app = DocumentsApplicationsSerializer(data={'document_id': pk, 'application_id': application.application_id})
    except Exception as e:
        print(e)
        print('create')
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

@api_view(['Delete']) 
def delete_document(request, pk, format=None):    
    """
    Удаляет информацию о документе - устанавливает статус 'deleted'
    """
    document = get_object_or_404(Documents, pk=pk)
    document.document_status = 'deleted'
    document.save()
    serializer = DocumentsSerializer(document)
    return Response(serializer.data)

@api_view(['Get']) 
def get_applications(request, format=None):
    """
    Возвращает список заявок
    """
    print('get')
    stocks = NameChangeApplications.objects.all()
    serializer = ApplicationsSerializer(stocks, many=True)
    return Response(serializer.data)

@api_view(['Get']) 
def get_application(request, pk, format=None):
    stock = get_object_or_404(NameChangeApplications, pk=pk)
    if request.method == 'GET':
        """
        Возвращает информацию об одной заявке
        """
        serializer = ApplicationsSerializer(stock)
        return Response(serializer.data)

@api_view(['PUT']) 
def put_applications_moderator(request, pk, format=None):
    """
    Обновляет информацию о документе модератор
    """
    application = get_object_or_404(NameChangeApplications, pk=pk)
    if request.data.get('application_status') not in ['in_progress', 'completed', 'canceled']:
        return Response({"error": "Invalid status value."}, status=400)
    application.application_status = request.data.get('application_status')
    if request.data.get('application_status') in ['completed', 'canceled']:
        application.date_of_application_completion = datetime.now()
    else:
        application.date_of_application_acceptance = datetime.now()
    serializer = ApplicationsSerializer(application, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
   
@api_view(['PUT']) 
def put_applications_client(request, pk, format=None):
    """
    Обновляет информацию о документе клиент
    """
    application = get_object_or_404(NameChangeApplications, pk=pk)
    if request.data.get('application_status') not in ['created', 'deleted']:
        return Response({"error": "Invalid status value."}, status=400)
    if request.data.get('application_status') == 'deleted':
        application.date_of_application_completion = datetime.now()
    application.application_status = request.data.get('application_status')
    serializer = ApplicationsSerializer(application, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
@api_view(['Delete']) 
def delete_application(request, pk, formate=None):
    application = get_object_or_404(NameChangeApplications, pk=pk)
    application.application_status = 'deleted'
    application.save()
    serializer = ApplicationsSerializer(application) 
    return Response(serializer.data)
    
@api_view(["Delete"]) 
def delete_document_application(request, document_id, application_id, formate=None):
    document_application = get_object_or_404(DocumentsApplications, document_id=document_id, application_id=application_id)
    document_application.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
    