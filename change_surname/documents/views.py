from django.shortcuts import render, redirect
from .models import Documents
import psycopg2
from django.conf import settings
from django.db.models import Q

    
def DeletedDoc(request, doc_id):
    status = 'deleted'
    conn = psycopg2.connect(database=settings.DATABASES['default']['NAME'], user=settings.DATABASES['default']['USER'], password=settings.DATABASES['default']['PASSWORD'])
    cursor = conn.cursor()
    cursor.execute(f"UPDATE documents SET document_status = '{status}' WHERE document_id = {doc_id}")
    conn.commit()
    return redirect('search')
    

def GetDocument(request, name):
    return render(request, 'document.html', {'data' : {
        'doc': Documents.objects.get(document_name__exact=name),
}})
    
def search(request):
    docs = Documents.objects.all()
    print(docs)
    inputValue = request.GET.get('search_query')
    query = inputValue
    if query:  
        filtered_items = Documents.objects.filter(
            Q(document_status = 'active'),
            Q(document_title__contains = query.lower())|Q(document_title__contains = query.upper())|Q(document_title__contains = query)
        )
    else:
        filtered_items = Documents.objects.all()  
    return render(request, 'documents.html', {'items': filtered_items,})
