# Generated by Django 4.1.7 on 2023-03-03 00:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kinokino', '0002_movie'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='name',
            field=models.CharField(max_length=50),
        ),
    ]