# Generated by Django 4.1.7 on 2023-03-05 04:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kinokino', '0036_collection'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='name',
            field=models.CharField(default=None, max_length=50),
        ),
    ]
