# Generated by Django 3.0.8 on 2021-01-28 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0041_auto_20210128_0155'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={'get_latest_by': 'date_created', 'ordering': ('name',)},
        ),
        migrations.AlterField(
            model_name='data',
            name='date_created',
            field=models.DateField(db_index=True),
        ),
    ]
