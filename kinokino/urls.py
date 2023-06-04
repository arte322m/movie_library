from django.urls import path
from . import views

app_name = 'kinokino'
urlpatterns = [
    path('', views.main, name='main'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/registration/', views.registration, name='registration'),
    path('switch_theme/', views.switch_theme, name='switch_theme'),
    path('searching/', views.searching, name='searching'),
    path('search/<str:search_text>', views.search, name='search'),
    path('add/', views.add_movie, name='add_movie'),
    path('favorite/', views.favorite, name='favorite'),
    path('movies/', views.all_movies, name='all_movies'),
    path('movies/<int:movie_id>', views.all_seasons, name='all_seasons'),
    path('movies/<int:movie_id>/<int:season_id>', views.all_episodes, name='all_episodes'),
    path('favorite_movie/', views.favorite_movie, name='favorite_movie'),
]
