# Generated by Django 4.2.4 on 2023-09-25 11:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0002_documents_delete_docs'),
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('second_name', models.CharField(max_length=50)),
                ('login', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=50)),
                ('email', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'Users',
            },
        ),
        migrations.AlterModelOptions(
            name='documents',
            options={'verbose_name_plural': 'Documents'},
        ),
        migrations.CreateModel(
            name='NameChangeApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_of_application_creation', models.DateTimeField(auto_now_add=True)),
                ('date_of_application_acceptance', models.DateTimeField()),
                ('date_of_application_completion', models.DateTimeField()),
                ('new_surname', models.CharField(max_length=50)),
                ('reason_for_change', models.TextField(blank=True)),
                ('application_status', models.CharField(choices=[('created', 'Создан'), ('in_progress', 'В работе'), ('completed', 'Завершен'), ('canceled', 'Отменен'), ('deleted', 'Удален')], max_length=20)),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='documents.users')),
            ],
            options={
                'verbose_name_plural': 'NameChangeApplication',
            },
        ),
        migrations.CreateModel(
            name='DocumentsApplications',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('application_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='documents.namechangeapplication')),
                ('documnet_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='documents.documents')),
            ],
            options={
                'verbose_name_plural': 'DocumentsApplications',
            },
        ),
    ]