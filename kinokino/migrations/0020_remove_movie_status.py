# Generated by Django 4.1.7 on 2023-03-04 02:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kinokino', '0019_remove_movie_favorite_movie_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movie',
            name='status',
        ),
    ]
