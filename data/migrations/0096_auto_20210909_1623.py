# Generated by Django 3.0.8 on 2021-09-09 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0095_exportcomments_date'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Keyword',
        ),
        migrations.AlterField(
            model_name='exportcomments',
            name='status',
            field=models.IntegerField(choices=[(0, 'Not Running'), (1, 'Running'), (2, 'Error'), (3, 'Done'), (4, 'Queued')], default=0),
        ),
        migrations.AlterField(
            model_name='twittersearch',
            name='status',
            field=models.IntegerField(choices=[(0, 'Not Running'), (1, 'Running'), (2, 'Error'), (3, 'Done'), (4, 'Queued')], default=0),
        ),
    ]
