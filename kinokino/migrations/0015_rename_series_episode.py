# Generated by Django 4.1.7 on 2023-03-03 15:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kinokino', '0014_season_episodes_count'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Series',
            new_name='Episode',
        ),
    ]