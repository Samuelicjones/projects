# Generated by Django 5.1.1 on 2024-09-24 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0005_alter_team_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
    ]
