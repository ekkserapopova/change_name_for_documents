# Generated by Django 4.2.4 on 2023-12-24 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0009_alter_documents_document_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documents',
            name='document_name',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='documents',
            name='document_status',
            field=models.CharField(choices=[('active', 'Действует'), ('deleted', 'Удалено'), ('trash', 'В корзине')], default='active', max_length=20, null=True),
        ),
    ]