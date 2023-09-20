from django.shortcuts import render, redirect
from .models import Docs
    
def DeletedDoc(request, doc_id):
    object = Docs.objects.get(id=int(doc_id))
    object.status = 'deleted'
    object.save()
    docs = Docs.objects.all()
    return redirect('search')
    

def GetDocument(request, name):
    docs = Docs.objects.all()
    for doc in docs:
        if doc.name == name:
            docs = doc
            break
    return render(request, 'document.html', {'data' : {
        'doc': docs,
}})
    
def search(request):
    docs = Docs.objects.all()
    inputValue = request.GET.get('search_query') 
    query = inputValue
    if query:  
        filtered_items = [doc for doc in docs if query.lower() in doc.title.lower() ]  
    else:
        filtered_items = docs  

    return render(request, 'documents.html', {'items': filtered_items,})

# Create your views here.
