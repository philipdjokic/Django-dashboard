# Generated by Django 3.0.8 on 2020-11-16 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0032_auto_20201116_1737'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='label',
            field=models.CharField(blank=True, max_length=300, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='keyword',
            name='label',
            field=models.CharField(blank=True, max_length=300, null=True, unique=True),
        ),
    ]
