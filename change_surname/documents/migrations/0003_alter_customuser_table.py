# Generated by Django 4.2.4 on 2023-11-27 00:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0002_customuser_first_name_customuser_last_name_and_more'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='customuser',
            table='users',
        ),
    ]