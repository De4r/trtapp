# Generated by Django 2.2.7 on 2019-12-11 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UploadedFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(max_length=100)),
                ('file_object', models.FileField(upload_to='files')),
                ('upload_date', models.DateField(auto_now_add=True)),
            ],
        ),
    ]
