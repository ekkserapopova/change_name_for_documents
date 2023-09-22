from django.db import models
from django.conf import settings


# Create your models here.

STATUS_DOCS = [
    ('active', 'Действует'),
    ('deleted', 'Удалено'),
]

class Documents(models.Model):
    document_title = models.CharField(max_length=100)
    document_name = models.CharField(max_length=100)
    document_overview = models.TextField(blank=True)
    document_description = models.TextField(blank=True)
    document_image = models.ImageField(upload_to='change_surname/documents/static', default='')
    document_status = models.CharField(max_length=20,choices=STATUS_DOCS)
    
    def __str__(self):
        return f"{self.id}"



