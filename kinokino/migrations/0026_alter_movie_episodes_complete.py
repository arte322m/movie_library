# Generated by Django 4.1.7 on 2023-03-04 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kinokino', '0025_movie_episodes_complete'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='episodes_complete',
            field=models.IntegerField(default=0, max_length=models.IntegerField(null=True), null=True),
        ),
    ]