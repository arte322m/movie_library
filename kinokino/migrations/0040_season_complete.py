# Generated by Django 4.1.7 on 2023-03-20 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kinokino', '0039_episode_complete'),
    ]

    operations = [
        migrations.AddField(
            model_name='season',
            name='complete',
            field=models.ManyToManyField(to='kinokino.userprofile'),
        ),
    ]