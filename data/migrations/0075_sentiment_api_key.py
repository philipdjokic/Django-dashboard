# Generated by Django 3.0.8 on 2021-06-21 21:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0074_project_api_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='sentiment',
            name='api_key',
            field=models.TextField(default=''),
        ),
    ]