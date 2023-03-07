from django.urls import path
from . import views

app_name = 'kinokino'
urlpatterns = [
    path('', views.main, name='main'),
    path('accounts/logout', views.logout_view, name='logout'),
    path('accounts/login', views.login_view, name='login'),
    path('accounts/registration', views.registration, name='registration'),
    path('switch_theme', views.switch_theme, name='switch_theme'),
    path('searching', views.searching, name='searching'),
    path('search/<str:search_text>', views.search, name='search'),
    path('add', views.add_movie, name='add_movie'),
    path('favorite', views.favorite, name='favorite'),
    path('movies', views.all_movies, name='all_movies'),
    path('movies/<int:movie_id>', views.all_seasons, name='all_seasons'),
    path('movies/<int:movie_id>/<int:season_id>', views.all_episodes, name='all_episodes'),
    path('favorite_movie', views.favorite_movie, name='favorite_movie'),
    path('add_status', views.add_status, name='add_status'),
    path('delete_status', views.delete_status, name='delete_status'),
    path('collection', views.collections, name='collections'),
    path('collection/change_collection/<int:collection_id>', views.change_collection, name='change_collection'),
    path('collection/change_collection/add_movie_in_collection', views.add_movie_in_collection,
         name='add_movie_in_collection'),
    path('collection/<int:collection_id>', views.collection_detail, name='collection_detail'),
    path('collection/create_collection', views.create_collection, name='create_collection'),
    path('bookmarks/', views.bookmarks, name='bookmarks'),
    path('bookmarks/completed/', views.bookmarks_completed, name='bookmarks_completed'),
    path('bookmarks/planned_to_watch/', views.bookmarks_planned_to_watch, name='bookmarks_planned_to_watch'),
    path('bookmarks/watching/', views.bookmarks_watching, name='bookmarks_watching'),
]
