# Generated by Django 4.1.7 on 2023-03-03 05:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kinokino', '0008_remove_series_movie_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='release_year_end',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='movie',
            name='release_year_start',
            field=models.DateField(null=True),
        ),
    ]