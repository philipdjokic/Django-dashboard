# Generated by Django 2.0.5 on 2020-08-10 21:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0007_charts'),
    ]

    operations = [
        migrations.RenameField(
            model_name='charts',
            old_name='Project',
            new_name='project',
        ),
    ]