# Generated by Django 3.0.8 on 2021-04-27 23:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0054_auto_20210427_2301'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sentiment',
            old_name='repustate_id',
            new_name='rule_id',
        ),
    ]
