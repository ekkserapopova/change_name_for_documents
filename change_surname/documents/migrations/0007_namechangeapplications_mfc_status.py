# Generated by Django 4.2.4 on 2023-12-21 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0006_alter_documents_document_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='namechangeapplications',
            name='mfc_status',
            field=models.CharField(default=' ', max_length=15),
        ),
    ]
