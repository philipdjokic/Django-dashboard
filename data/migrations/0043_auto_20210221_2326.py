# Generated by Django 3.0.8 on 2021-02-21 23:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0042_auto_20210128_1540'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='country',
            options={'ordering': ('label',), 'verbose_name_plural': 'Countries'},
        ),
        migrations.AlterModelOptions(
            name='source',
            options={'ordering': ('label',)},
        ),
        migrations.CreateModel(
            name='Summary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateField(auto_now=True)),
                ('title', models.CharField(default='', max_length=80)),
                ('description', models.TextField()),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.Project')),
            ],
        ),
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateField(auto_now=True)),
                ('handled', models.BooleanField(default=False)),
                ('title', models.CharField(default='', max_length=80)),
                ('description', models.TextField()),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data.Project')),
            ],
        ),
    ]
