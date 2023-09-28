from django.contrib import admin
from .models import Documents, Users, NameChangeApplications, DocumentsApplications

admin.site.register(Documents)
admin.site.register(Users)
admin.site.register(NameChangeApplications)
admin.site.register(DocumentsApplications)


# Register your models here.
