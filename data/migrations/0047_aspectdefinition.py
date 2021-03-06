# Generated by Django 3.0.8 on 2021-04-08 22:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0046_auto_20210408_2153'),
    ]

    operations = [
        migrations.CreateModel(
            name='AspectDefinition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rule_name', models.CharField(max_length=80)),
                ('definition', models.CharField(max_length=80)),
                ('aspect_model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.AspectModel')),
            ],
        ),
    ]
