from django.contrib import admin
from .models import Documents, Users, NameChangeApplication, DocumentsApplications

admin.site.register(Documents)
admin.site.register(Users)
admin.site.register(NameChangeApplication)
admin.site.register(DocumentsApplications)


# Register your models here.
