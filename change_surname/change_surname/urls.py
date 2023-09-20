from django.contrib import admin
from django.urls import path
from documents import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('documents/deleted/<int:doc_id>/', views.DeletedDoc, name='deleted'),
    path('documents/', views.search, name='search'),
    path('documents/<slug:name>/', views.GetDocument, name='doc_url'),
]
