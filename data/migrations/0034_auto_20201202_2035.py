# Generated by Django 3.0.8 on 2020-12-02 20:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0033_auto_20201116_1804'),
    ]

    operations = [
        migrations.CreateModel(
            name='CountryNew',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=300, null=True, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Countries',
            },
        ),
        migrations.AlterField(
            model_name='data',
            name='country',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='data.CountryNew'),
        ),
        migrations.DeleteModel(
            name='Country',
        ),
    ]
