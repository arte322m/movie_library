# Generated by Django 4.1.7 on 2023-03-03 00:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kinokino', '0003_alter_movie_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Series',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('tv_series_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kinokino.movie')),
            ],
        ),
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('series', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kinokino.series')),
                ('tv_series_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kinokino.movie')),
            ],
        ),
    ]
