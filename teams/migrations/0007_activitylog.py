# Generated by Django 5.1.1 on 2024-11-12 01:21

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0006_alter_team_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('created', 'Created'), ('updated', 'Updated'), ('deleted', 'Deleted'), ('completed', 'Completed')], max_length=20)),
                ('affected_object', models.CharField(max_length=255)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('team_member', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='teams.teammember')),
            ],
        ),
    ]
