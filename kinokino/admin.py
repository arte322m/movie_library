from django.contrib import admin

from kinokino.models import Movie, UserProfile, Season, Episode, MovieStatus, CompletedEpisode

admin.site.register(UserProfile)
admin.site.register(Movie)
admin.site.register(Season)
admin.site.register(Episode)
admin.site.register(MovieStatus)
admin.site.register(CompletedEpisode)
