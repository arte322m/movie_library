# Generated by Django 4.1.7 on 2023-03-05 03:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kinokino', '0034_alter_moviestatus_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movie',
            name='episodes_complete',
        ),
    ]