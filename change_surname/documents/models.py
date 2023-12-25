from django.db import models
from django.conf import settings
from django.contrib.auth.models import UserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission


# Create your models here.

ROLES = [
    ('client', 'Клиент'),
    ('moderator', 'Модератор'),
]

STATUS_DOCS = [
    ('active', 'Действует'),
    ('deleted', 'Удалено'),
    ('trash', 'В корзине')
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
    document_name = models.CharField(max_length=100, null=True)
    document_overview = models.TextField(blank=True)
    document_description = models.TextField(blank=True)
    document_image = models.CharField(max_length=10000, default='not_found.jpg', blank=True, null=True)
    document_price = models.FloatField()
    document_status = models.CharField(max_length=20,choices=STATUS_DOCS, default='active', null=True)
    
    class Meta:
        db_table = 'documents'
        verbose_name_plural = "Documents"
    
    def __str__(self):
        return self.document_title

class NewUserManager(UserManager):
    def create_user(self,email,password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address')
        
        email = self.normalize_email(email) 
        user = self.model(email=email, **extra_fields) 
        user.set_password(password)
        user.save(using=self.db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(("email адрес"), unique=True)
    password = models.CharField(max_length=150, verbose_name="Пароль")   
    first_name = models.CharField(max_length=150, verbose_name="Имя")  
    last_name = models.CharField(max_length=150, verbose_name="Фамилия")  
    otchestvo = models.CharField(max_length=150, verbose_name="Отчетсво") 
    pasport = models.CharField(max_length=11, verbose_name="Паспортные данные(серия и номер)") 
    is_staff = models.BooleanField(default=False, verbose_name="Является ли пользователь менеджером?")
    is_superuser = models.BooleanField(default=False, verbose_name="Является ли пользователь админом?")
    is_active = models.BooleanField(default=True, verbose_name="Активен ли пользователь?")
    groups = models.ManyToManyField(Group, verbose_name="Группы", blank=True, related_name="customuser_groups")
    USERNAME_FIELD = 'email'
    user_permissions = models.ManyToManyField(Permission, verbose_name="Права доступа", blank=True, related_name="customuser_user_permissions")

    objects =  NewUserManager()
    
    class Meta:
        db_table = 'users'



class NameChangeApplications(models.Model):
    application_id = models.AutoField(primary_key=True)
    client_id = models.ForeignKey(CustomUser, models.DO_NOTHING, related_name='client')
    moderator_id = models.ForeignKey(CustomUser, models.DO_NOTHING, related_name='moderator')
    date_of_application_creation = models.DateTimeField(auto_now_add=True)
    date_of_application_acceptance = models.DateTimeField(blank=True, null=True)
    date_of_application_completion = models.DateTimeField(blank=True, null=True)
    new_surname = models.CharField(max_length=50)
    reason_for_change = models.TextField()
    application_status = models.CharField(max_length=20,choices=STATUS_APPS, default='created')
    mfc_status = models.CharField(max_length=15, default=" ")
    
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
