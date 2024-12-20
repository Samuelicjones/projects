# Generated by Django 5.1.1 on 2024-10-22 18:34

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('jobs', '0002_rename_priorty_job_priority'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_details', models.TextField()),
                ('payment_method', models.CharField(choices=[('card', 'Card'), ('cash', 'Cash'), ('check', 'Check'), ('billed', 'Billed')], max_length=10)),
                ('payment_received', models.BooleanField(default=False)),
                ('report_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('job', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='jobs.job')),
            ],
        ),
    ]
