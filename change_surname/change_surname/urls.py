from django.contrib import admin
from documents import views
from django.urls import include, path
from rest_framework import routers
router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path(r'documents/', views.get_documents, name='documents-active-list'),
    path(r'documents/post/', views.post_document, name='documents-post'),
    path(r'documents/<int:pk>/', views.get_document, name='documents-detail'),
    path(r'documents/<int:pk>/put/', views.put_document, name='documents-put'),
    path(r'documents/<int:pk>/post/', views.post_application, name='documents-post'),
    path(r'documents/<int:pk>/delete/', views.delete_document, name='document-delete'),
    
    path(r'applications/', views.get_applications, name='applications-list'),
    path(r'applications/<int:pk>/', views.get_application, name='application-detail'),
    path(r'applications/<int:pk>/put/moderator/', views.put_applications_moderator, name='application-put_by-moderator'),
    path(r'applications/<int:pk>/put/client/', views.put_applications_client, name='application-put_by-moderator'),
    path(r'applications/<int:pk>/put/', views.put_application),
    path(r'applications/<int:pk>/delete/', views.delete_application, name='application-delete'),

    path(r'documents_applicaions/<int:document_id>/<int:application_id>/delete/', views.delete_document_application),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('admin/', admin.site.urls),
]
