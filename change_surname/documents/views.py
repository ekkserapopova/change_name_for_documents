from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from .serializers import DocumentsSerializer, ApplicationsSerializer, DocumentsApplicationsSerializer
from .models import Documents, NameChangeApplications, DocumentsApplications
from rest_framework.decorators import api_view
from datetime import datetime
from minio import Minio
from django.db.models import Q, CharField
from django.db.models.functions import Lower,Upper

client = Minio(endpoint="localhost:9000",   
               access_key='minio',          
               secret_key='minio124',       
               secure=False)  


@api_view(['Get']) 
def get_documents(request, format=None):
    """
    Возвращает список активных документов 
    """
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
        documents = documents.filter(Q(document_price__gte = min_price))
        
    if max_price:
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

@api_view(['Get']) 
def get_document(request, pk, format=None):
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

@api_view(['Post']) 
def post_document(request, format=None):    
    """
    Добавляет новый документ
    """
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

@api_view(['PUT']) 
def put_document(request, pk, format=None):
    """
    Обновляет информацию о документе
    """
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
    startdate = request.GET.get("startdate")
    enddate = request.GET.get("enddate")
    statuses = request.GET.get("status")
    applications = NameChangeApplications.objects.all()
    
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

@api_view(['Get']) 
def get_application(request, pk, format=None):
    application = get_object_or_404(NameChangeApplications, pk=pk)
    """
    Возвращает информацию об одной заявке
    """
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
    
@api_view(['PUT'])
def put_application(request, pk, format=None):
    """
    Обновляет информацию в заявке - surname and reason
    """
    application = get_object_or_404(NameChangeApplications, pk=pk)
    serializer = ApplicationsSerializer(application, data=request.data, partial=True)
    if application.application_status != 'created':
        return Response({"error": "Неверный статус."}, status=400)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    

@api_view(['PUT']) 
def put_applications_moderator(request, pk, format=None):
    """
    Обновляет информацию о документе модератор
    """
    application = get_object_or_404(NameChangeApplications, pk=pk)
    print(application.application_status)
    if request.data['application_status'] not in ['completed', 'canceled'] or application.application_status == 'created':
        return Response({"error": "Неверный статус."}, status=400)
    application.application_status = request.data['application_status']
    application.date_of_application_completion = datetime.now()
    serializer = ApplicationsSerializer(application, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PUT']) 
def put_applications_client(request, pk, format=None):
    """
    Обновляет информацию о документе клиент
    """
    application = get_object_or_404(NameChangeApplications, pk=pk)
    if request.data['application_status'] != 'in_progress' or application.application_status != 'created':
        return Response({"error": "Неверный статус."}, status=400)
    application.application_status = request.data['application_status']
    application.date_of_application_acceptance = datetime.now()
    serializer = ApplicationsSerializer(application, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['Delete']) 
def delete_application(request, pk, formate=None):
    application = get_object_or_404(NameChangeApplications, pk=pk)
    if application.application_status != 'created':
         return Response({"error": "Неверный статус."}, status=400)       
    application.application_status = 'deleted'
    application.date_of_application_completion = datetime.now()
    application.save()
    serializer = ApplicationsSerializer(application) 
    return Response(serializer.data)
    
@api_view(["Delete"]) 
def delete_document_application(request, document_id, application_id, formate=None):
    document_application = get_object_or_404(DocumentsApplications, document_id=document_id, application_id=application_id)
    document_application.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
    