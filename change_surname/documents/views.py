from django.shortcuts import render, redirect
from .models import Documents
import psycopg2
from django.conf import settings
    
def DeletedDoc(request, doc_id):
    status = 'deleted'
    conn = psycopg2.connect(database=settings.DATABASES['default']['NAME'], user=settings.DATABASES['default']['USER'], password=settings.DATABASES['default']['PASSWORD'])
    cursor = conn.cursor()
    cursor.execute(f"UPDATE documents_documents SET document_status = '{status}' WHERE id = {doc_id}")
    conn.commit()
    return redirect('search')
    

def GetDocument(request, name):
    docs = Documents.objects.all()
    for doc in docs:
        if doc.document_name == name:
            docs = doc
            break
    return render(request, 'document.html', {'data' : {
        'doc': docs,
}})
    
def search(request):
    docs = Documents.objects.all()
    print(docs)
    inputValue = request.GET.get('search_query') 
    query = inputValue
    if query:  
        filtered_items = [doc for doc in docs if query.lower() in doc.document_title.lower() ]  
    else:
        filtered_items = docs  

    return render(request, 'documents.html', {'items': filtered_items,})

# Create your views here.
