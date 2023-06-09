import datetime

from rest_framework.views import Response
from rest_framework import status
from kinokino.kinopoisk_parser import search_series_by_id
from kinokino.models import UserProfile, Movie, UserMovieStatus, Season, Episode


def add_movie_episodes(username: str,
                       name: str,
                       kin_id: int,
                       year: int,
                       movie_type: str,
                       preview_url: str,
                       year_start: int,
                       year_end: int):

    if not year_start:
        year_start = None
    if not year_end:
        year_end = None
    user = UserProfile.objects.get(user__username=username)
    try:
        if Movie.objects.get(kinopoisk_id=kin_id):
            movie = Movie.objects.get(kinopoisk_id=kin_id)
            try:
                if UserMovieStatus.objects.get(user=user, movie=movie):
                    return Response(status=status.HTTP_200_OK)
            except UserMovieStatus.DoesNotExist:
                UserMovieStatus.objects.create(user=user, status=UserMovieStatus.PLANNED_TO_WATCH, movie=movie)
                return Response(status=status.HTTP_201_CREATED)
    except Movie.DoesNotExist:

        if year_start:
            all_episode_count = 0
            seasons = []
            search_result = search_series_by_id(kin_id)
            new_movie = Movie.objects.create(
                name=name,
                kinopoisk_id=kin_id,
                year=year,
                preview_url=preview_url,
                type=movie_type,
                release_year_start=year_start,
            )
            if year_end:
                new_movie.release_year_end = year_end
            new_movie.save()
            for season_info in search_result:
                number = season_info['number']
                if number == 0:
                    continue
                if number in seasons:
                    continue
                seasons.append(number)
                episodes_count = len(season_info['episodes'])
                all_episode_count += episodes_count
                new_season = Season.objects.create(
                    movie_id=new_movie,
                    number=number,
                    episodes_count=episodes_count
                )
                for episodes_info in season_info['episodes']:
                    number = episodes_info['number']
                    # if episodes_info['name']:
                    #     episode_name = episodes_info['name']
                    # else:
                    #     episode_name = episodes_info['enName']
                    # date_str = episodes_info['date'][:10]
                    # date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                    Episode.objects.create(
                        number=number,
                        # date=date,
                        # name=episode_name,
                        season=new_season,
                    )
                new_movie.episodes_count = all_episode_count
                new_movie.seasons_count = len(seasons)
                new_movie.save()
        else:
            new_movie = Movie.objects.create(
                name=name,
                kinopoisk_id=kin_id,
                type=movie_type,
                preview_url=preview_url,
                year=year,
            )
        UserMovieStatus.objects.create(user=user, status=UserMovieStatus.PLANNED_TO_WATCH, movie=new_movie)

    return Response(status=status.HTTP_201_CREATED)
