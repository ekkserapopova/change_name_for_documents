# Generated by Django 4.2.4 on 2023-09-28 19:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0008_alter_namechangeapplication_date_of_application_acceptance_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='documents',
            name='id',
        ),
        migrations.RemoveField(
            model_name='documentsapplications',
            name='id',
        ),
        migrations.RemoveField(
            model_name='users',
            name='id',
        ),
        migrations.AddField(
            model_name='documents',
            name='document_id',
            field=models.AutoField(primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='users',
            name='role',
            field=models.CharField(choices=[('client', 'Клиент'), ('moderator', 'Модератор')], default='client', max_length=9),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='users',
            name='user_id',
            field=models.AutoField(primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='documents',
            name='document_image',
            field=models.ImageField(default='change_surname/documents/static/not_found.jpeg', upload_to='change_surname/documents/static'),
        ),
        migrations.AlterField(
            model_name='documentsapplications',
            name='documnet_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='documents.documents'),
        ),
        migrations.AlterModelTable(
            name='documents',
            table='documents',
        ),
        migrations.AlterModelTable(
            name='documentsapplications',
            table='documents_applications',
        ),
        migrations.AlterModelTable(
            name='users',
            table='users',
        ),
        migrations.CreateModel(
            name='NameChangeApplications',
            fields=[
                ('application_id', models.AutoField(primary_key=True, serialize=False)),
                ('date_of_application_creation', models.DateTimeField(auto_now_add=True)),
                ('date_of_application_acceptance', models.DateTimeField(blank=True, null=True)),
                ('date_of_application_completion', models.DateTimeField(blank=True, null=True)),
                ('new_surname', models.CharField(max_length=50)),
                ('reason_for_change', models.TextField()),
                ('application_status', models.CharField(choices=[('created', 'Создан'), ('in_progress', 'В работе'), ('completed', 'Завершен'), ('canceled', 'Отменен'), ('deleted', 'Удален')], default='created', max_length=20)),
                ('client_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='client', to='documents.users')),
                ('moderator_id', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='moderator', to='documents.users')),
            ],
            options={
                'verbose_name_plural': 'NameChangeApplication',
                'db_table': 'name_change_applications',
            },
        ),
        migrations.AlterField(
            model_name='documentsapplications',
            name='application_id',
            field=models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='documents.namechangeapplications'),
        ),
        migrations.DeleteModel(
            name='NameChangeApplication',
        ),
    ]