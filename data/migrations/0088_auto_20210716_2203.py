# Generated by Django 3.0.8 on 2021-07-16 22:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0087_data_search'),
    ]

    operations = [
        migrations.RunSQL("set default_text_search_config = 'pg_catalog.simple';")
    ]
