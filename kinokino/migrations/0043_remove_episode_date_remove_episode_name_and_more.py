# Generated by Django 4.1.7 on 2023-06-09 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kinokino', '0042_rename_completedepisodes_completedepisode'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='episode',
            name='date',
        ),
        migrations.RemoveField(
            model_name='episode',
            name='name',
        ),
        migrations.AddField(
            model_name='movie',
            name='complete',
            field=models.BooleanField(default=False),
        ),
    ]
