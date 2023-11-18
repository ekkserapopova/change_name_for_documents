from .models import Documents, NameChangeApplications, DocumentsApplications
from rest_framework import serializers
from rest_framework.views import APIView
from .models import CustomUser


class DocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Documents
        # Поля, которые мы сериализуем
        fields = "__all__"

class ApplicationsSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = NameChangeApplications
        # Поля, которые мы сериализуем
        fields = "__all__"
        
class DocumentsApplicationsSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = DocumentsApplications
        # Поля, которые мы сериализуем
        fields = ["document_id", "application_id"]
        
class UserSerializer(serializers.ModelSerializer):
    is_staff = serializers.BooleanField(default=False, required=False)
    is_superuser = serializers.BooleanField(default=False, required=False)
    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'is_staff', 'is_superuser']
        # fields = "__all__"