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
    MOVIE = 'movie'
    TV_SERIES = 'tv-series'
    CARTOON = 'cartoon'
    ANIME = 'anime'
    ANIMATED_SERIES = 'animated-series'
    TV_SHOW = 'tv-show'
    TYPE_MOVIE = [
        (MOVIE, 'Movie'),
        (TV_SERIES, 'Tv-Series'),
        (CARTOON, 'Cartoon'),
        (ANIME, 'Anime'),
        (ANIMATED_SERIES, 'Animated-Series'),
        (TV_SHOW, 'TV-Show'),
    ]
    NONE = 'Не смотрю'
    PLANNED_TO_WATCH = 'Хочу посмотреть'
    WATCHING = 'Смотрю'
    COMPLETED = 'Просмотрено'
    MOVIE_STATUS = [
        (NONE, 'не смотрю'),
        (PLANNED_TO_WATCH, 'хочу посмотреть'),
        (WATCHING, 'смотрю'),
        (COMPLETED, 'просмотрено'),
    ]
    kinopoisk_id = models.IntegerField(default=None)
    name = models.CharField(max_length=50)
    year = models.IntegerField(default=None)
    type = models.CharField(max_length=15, choices=TYPE_MOVIE, default=None, null=True)
    seasons_count = models.IntegerField(null=True)
    release_year_start = models.IntegerField(null=True)
    release_year_end = models.IntegerField(null=True)
    status = models.CharField(max_length=16, choices=MOVIE_STATUS, default=NONE)


class Season(models.Model):
    movie_id = models.ForeignKey(Movie, on_delete=models.CASCADE)
    number = models.IntegerField(default=None)
    episodes_count = models.IntegerField(default=None)


class Episode(models.Model):
    number = models.IntegerField(default=None)
    date = models.DateTimeField(default=None)
    name = models.CharField(max_length=50)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, default=None)
