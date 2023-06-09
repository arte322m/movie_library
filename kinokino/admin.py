from django.contrib import admin

from kinokino.models import Movie, UserProfile, Season, Episode, UserMovieStatus, CompletedEpisode

admin.site.register(UserProfile)
admin.site.register(Movie)
admin.site.register(Season)
admin.site.register(Episode)
admin.site.register(UserMovieStatus)
admin.site.register(CompletedEpisode)
