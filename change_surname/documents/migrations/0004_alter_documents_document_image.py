# Generated by Django 4.2.4 on 2023-12-02 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0003_alter_customuser_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documents',
            name='document_image',
            field=models.ImageField(default='not_found.jpg', max_length=10000, upload_to=''),
        ),
    ]