# Generated by Django 3.0.8 on 2021-07-05 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0082_entity_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='entity',
            name='aliases',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='entity',
            name='api_key',
            field=models.TextField(default=''),
        ),
    ]
