from .models import Documents, NameChangeApplications, DocumentsApplications
from rest_framework import serializers
from rest_framework.views import APIView


class DocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        # title_lower = serializers.CharField()
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