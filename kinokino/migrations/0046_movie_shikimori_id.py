# Generated by Django 4.1.7 on 2023-06-16 00:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kinokino', '0045_rename_moviestatus_usermoviestatus_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='shikimori_id',
            field=models.IntegerField(default=None, null=True),
        ),
    ]