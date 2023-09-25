from django.db import models
from django.conf import settings


# Create your models here.

STATUS_DOCS = [
    ('active', 'Действует'),
    ('deleted', 'Удалено'),
]

STATUS_APPS = [
    ('created', 'Создан'),
    ('in_progress', 'В работе'),
    ('completed', 'Завершен'),
    ('canceled', 'Отменен'),
    ('deleted', 'Удален'),
]

class Documents(models.Model):
    document_title = models.CharField(max_length=100, unique=True)
    document_name = models.CharField(max_length=100, unique=True)
    document_overview = models.TextField(blank=True)
    document_description = models.TextField(blank=True)
    document_image = models.ImageField(upload_to='change_surname/documents/static', default='')
    document_status = models.CharField(max_length=20,choices=STATUS_DOCS)
    
    class Meta:
        verbose_name_plural = "Documents"
    
    def __str__(self):
        return self.document_title
    
class Users(models.Model):
    first_name = models.CharField(max_length=50)
    second_name = models.CharField(max_length=50)
    login = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)
    email = models.CharField(max_length=50, unique=True)
    
    class Meta:
        verbose_name_plural = "Users"
    
    def __str__(self):
        return self.login

class NameChangeApplication(models.Model):
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    date_of_application_creation = models.DateTimeField(auto_now_add=True)
    date_of_application_acceptance = models.DateTimeField(blank=True, null=True)
    date_of_application_completion = models.DateTimeField(blank=True, null=True)
    new_surname = models.CharField(max_length=50)
    reason_for_change = models.TextField()
    application_status = models.CharField(max_length=20,choices=STATUS_APPS, default='created')
    
    class Meta:
        verbose_name_plural = "NameChangeApplication"

    def __str__(self):
        return f"{self.id}"
    
class DocumentsApplications(models.Model):
    application_id = models.ForeignKey(NameChangeApplication, on_delete=models.CASCADE)
    documnet_id = models.ForeignKey(Documents, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.application_id}, {self.documnet_id}"
    
    class Meta:
        verbose_name_plural = "DocumentsApplications"

