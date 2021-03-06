# Generated by Django 3.0.8 on 2020-10-01 20:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0018_merge_20200930_1812'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='twittersearch',
            name='completed',
        ),
        migrations.AddField(
            model_name='twittersearch',
            name='status',
            field=models.IntegerField(choices=[(0, 'Not Running'), (1, 'Running'), (2, 'Error'), (3, 'Done')], default=0),
        ),
        migrations.AlterField(
            model_name='twittersearch',
            name='query',
            field=models.CharField(help_text='See https://developer.twitter.com/en/docs/twitter-api/v1/tweets/filter-realtime/guides/premium-operators for info on setting up queries', max_length=80),
        ),
    ]
