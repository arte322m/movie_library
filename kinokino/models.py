from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    DARK = 'DARK'
    LIGHT = 'LIGHT'
    TYPE_OF_THEME = [
        (DARK, 'Dark'),
        (LIGHT, 'Light'),
    ]
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    type_of_theme = models.CharField(max_length=7, choices=TYPE_OF_THEME, default=DARK)


class Movie(models.Model):
    MOVIE = 'MOVIE'
    TV_SERIES = 'TV-SERIES'
    CARTOON = 'CARTOON'
    ANIME = 'ANIME'
    ANIMATED_SERIES = 'ANIMATED-SERIES'
    TV_SHOW = 'TV-SHOW'
    TYPE_MOVIE = [
        (MOVIE, 'movie'),
        (TV_SERIES, 'tv-series'),
        (CARTOON, 'cartoon'),
        (ANIME, 'anime'),
        (ANIMATED_SERIES, 'animated-series'),
        (TV_SHOW, 'tv-show'),
    ]
    kinopoisk_id = models.IntegerField
    name = models.CharField(max_length=50)
    year = models.IntegerField
    type = models.CharField(max_length=15, choices=TYPE_MOVIE)
    seasons_count = models.IntegerField(null=True)
    series_count = models.IntegerField(null=True)


class Season(models.Model):
    movie_id = models.ForeignKey(Movie, on_delete=models.CASCADE)
    number = models.IntegerField


class Series(models.Model):
    number = models.IntegerField
    date = models.DateField
    name = models.CharField(max_length=50)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, default=None)
