from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    DARK = 'DARK'
    LIGHT = 'LIGHT'
    TYPE_OF_THEME = [
        (DARK, 'Dark'),
        (LIGHT, 'Light'),
    ]
    KINOPOISK = 'Kinopoisk'
    SHIKIMORI = 'Shikimori'
    TYPE_OF_SEARCH = [
        (KINOPOISK, 'kinopoisk'),
        (SHIKIMORI, 'shikimori'),
    ]
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    type_of_theme = models.CharField(max_length=7, choices=TYPE_OF_THEME, default=DARK)
    type_of_search = models.CharField(max_length=10, choices=TYPE_OF_SEARCH,default=KINOPOISK)


class ShikimoriMovie(models.Model):
    ANONS = 'anons'
    ONGOING = 'ongoing'
    RELEASED = 'released'
    MOVIE_STATUS = [
        (ANONS, 'anons'),
        (ONGOING, 'ongoing'),
        (RELEASED, 'released'),
    ]
    shikimori_id = models.IntegerField(default=None, null=True)
    name = models.CharField(max_length=80)
    image = models.CharField(max_length=150)
    url = models.CharField(max_length=150)
    status = models.CharField(max_length=9, null=True, default=None, choices=MOVIE_STATUS)
    episodes = models.IntegerField(default=1)
    episodes_aired = models.IntegerField(default=None, null=True)
    aired_on = models.DateField()
    next_episode_date = models.DateField(null=True, default=None)
    released_on = models.DateField()
    favorite = models.ManyToManyField(UserProfile)


class CompletedEpisodeShikimori(models.Model):
    movie = models.ForeignKey(ShikimoriMovie, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    episode_complete_count = models.IntegerField(default=None, null=True)


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
    name = models.CharField(max_length=50)
    kinopoisk_id = models.IntegerField(default=None, null=True)
    preview_url = models.CharField(max_length=150, default=None, null=True)
    release_year_start = models.IntegerField(null=True)
    release_year_end = models.IntegerField(null=True)
    seasons_count = models.IntegerField(null=True)
    episodes_count = models.IntegerField(null=True)
    favorite = models.ManyToManyField(UserProfile)
    type = models.CharField(max_length=15, choices=TYPE_MOVIE, default=None, null=True)


class Season(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    number = models.IntegerField(default=None)
    episodes_count = models.IntegerField(default=None)
    episodes_released = models.IntegerField(default=None, null=True)
    complete = models.ManyToManyField(UserProfile)


class Episode(models.Model):
    number = models.IntegerField(default=None)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, default=None)


class UserMovieStatus(models.Model):
    NONE = '------'
    PLANNED_TO_WATCH = 'Запланировано'
    WATCHING = 'Смотрю'
    COMPLETED = 'Просмотрено'
    USER_MOVIE_STATUS = [
        (PLANNED_TO_WATCH, 'запланировано'),
        (WATCHING, 'смотрю'),
        (COMPLETED, 'просмотрено'),
    ]
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, default=None)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, default=None)
    status = models.CharField(max_length=16, choices=USER_MOVIE_STATUS, default=None)


class Collection(models.Model):
    name = models.CharField(max_length=50, default=None)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    movie = models.ManyToManyField(Movie)


class CompletedEpisode(models.Model):
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
