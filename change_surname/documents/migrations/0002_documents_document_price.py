# Generated by Django 4.2.4 on 2023-10-27 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='documents',
            name='document_price',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
    ]