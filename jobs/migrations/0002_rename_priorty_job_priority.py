# Generated by Django 5.1.1 on 2024-09-25 21:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='job',
            old_name='priorty',
            new_name='priority',
        ),
    ]