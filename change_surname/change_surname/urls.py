from django.contrib import admin
from documents import views
from django.urls import include, path
from rest_framework import routers
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet, basename='user')

schema_view = get_schema_view(
   openapi.Info(
      title="Documents API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', include(router.urls)),
    path(r'documents/', views.get_documents, name='documents-active-list'),
    path(r'documents/<int:pk>/', views.get_document, name='documents-detail'),
    path(r'documents/application/<int:pk>/', views.post_application, name='documents-post'),
    
    path(r'applications/', views.get_applications, name='applications-list'),
    path(r'applications/<int:pk>/', views.get_application, name='application-detail'),
    path(r'applications/<int:pk>/put/moderator/', views.put_applications_moderator, name='application-put_by-moderator'),
    path(r'applications/<int:pk>/put/client/', views.put_applications_client, name='application-put_by-moderator'),
    # path(r'applications/<int:pk>/delete/', views.delete_application, name='application-delete'),

    path(r'documents_applicaions/<int:document_id>/<int:application_id>/', views.delete_document_application),

    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('admin/', admin.site.urls),
    
    
    # path('swagger(?P<format>\.json|\.yaml)', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger.yaml/', schema_view.without_ui(cache_timeout=0), name='schema-yaml'),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('login',  views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
]
