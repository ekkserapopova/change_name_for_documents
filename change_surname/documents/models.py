from django.db import models
from django.conf import settings

# Create your models here.

ROLES = [
    ('client', 'Клиент'),
    ('moderator', 'Модератор'),
]

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
    document_id = models.AutoField(primary_key=True)
    document_title = models.CharField(max_length=100, unique=True)
    document_name = models.CharField(max_length=100, unique=True)
    document_overview = models.TextField(blank=True)
    document_description = models.TextField(blank=True)
    document_image = models.CharField(max_length=10000)
    document_price = models.FloatField()
    document_status = models.CharField(max_length=20,choices=STATUS_DOCS)
    
    class Meta:
        db_table = 'documents'
        verbose_name_plural = "Documents"
    
    def __str__(self):
        return self.document_title
    
class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    second_name = models.CharField(max_length=50)
    login = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)
    email = models.CharField(max_length=50, unique=True)
    role = models.CharField(max_length=9, choices=ROLES)
    
    class Meta:
        db_table = 'users'
        verbose_name_plural = "Users"
    
    def __str__(self):
        return self.login

class NameChangeApplications(models.Model):
    application_id = models.AutoField(primary_key=True)
    client_id = models.ForeignKey(Users, models.DO_NOTHING, related_name='client')
    moderator_id = models.ForeignKey(Users, models.DO_NOTHING, related_name='moderator')
    date_of_application_creation = models.DateTimeField(auto_now_add=True)
    date_of_application_acceptance = models.DateTimeField(blank=True, null=True)
    date_of_application_completion = models.DateTimeField(blank=True, null=True)
    new_surname = models.CharField(max_length=50)
    reason_for_change = models.TextField()
    application_status = models.CharField(max_length=20,choices=STATUS_APPS, default='created')
    
    class Meta:
        db_table = 'name_change_applications'
        verbose_name_plural = "NameChangeApplication"

    def __str__(self):
        return f"{self.application_id}"
    
class DocumentsApplications(models.Model):
    application_id = models.ForeignKey('NameChangeApplications', models.DO_NOTHING, primary_key=False)
    document_id = models.ForeignKey('Documents', models.DO_NOTHING, primary_key=False)
    
    def __str__(self):
        return f"{self.application_id}, {self.document_id}"
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['application_id', 'document_id'], name='pk')
        ]
        db_table = 'documents_applications'
        verbose_name_plural = "DocumentsApplications"
