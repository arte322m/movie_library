# Generated by Django 4.1.7 on 2023-03-04 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kinokino', '0027_alter_episode_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='date',
            field=models.DateTimeField(default=None),
        ),
    ]
