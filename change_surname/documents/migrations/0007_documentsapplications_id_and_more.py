# Generated by Django 4.2.4 on 2023-10-02 22:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0006_alter_documentsapplications_document_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentsapplications',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='documentsapplications',
            name='application_id',
            field=models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to='documents.namechangeapplications'),
        ),
    ]
