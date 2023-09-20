from django.db import models
from django.conf import settings


# Create your models here.

STATUS_DOCS = [
    ('active', 'Действует'),
    ('deleted', 'Удалено'),
]

class Docs(models.Model):
    title = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    overview = models.TextField(blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='change_surname/documents/static', default='')
    status = models.CharField(max_length=20,choices=STATUS_DOCS)
    
    def __str__(self):
        return f"{self.id}"



