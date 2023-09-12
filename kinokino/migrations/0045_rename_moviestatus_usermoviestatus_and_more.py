# Generated by Django 4.1.7 on 2023-06-09 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kinokino', '0044_season_episodes_released'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='MovieStatus',
            new_name='UserMovieStatus',
        ),
        migrations.RemoveField(
            model_name='movie',
            name='complete',
        ),
        migrations.AddField(
            model_name='movie',
            name='status',
            field=models.CharField(choices=[('anons', 'anons'), ('ongoing', 'ongoing'), ('released', 'released')], default=None, max_length=9, null=True),
        ),
    ]