# Generated by Django 2.2.7 on 2020-01-11 12:32

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_parametersmodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='parametersmodel',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]