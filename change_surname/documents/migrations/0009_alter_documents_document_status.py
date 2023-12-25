# Generated by Django 4.2.4 on 2023-12-23 00:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0008_alter_documents_document_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documents',
            name='document_status',
            field=models.CharField(choices=[('active', 'Действует'), ('deleted', 'Удалено'), ('trash', 'В корзине')], max_length=20),
        ),
    ]
