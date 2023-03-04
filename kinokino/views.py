import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from kinokino.kinopoisk_api_search import search_function
from kinokino.models import UserProfile, Movie, Episode, Season


@require_POST
def switch_theme(request):
    if request.user.is_authenticated:
        user = UserProfile.objects.get(user_id=request.user.id)
        if request.session['theme'] == UserProfile.DARK:
            user.type_of_theme = UserProfile.LIGHT
            user.save()
            request.session['theme'] = UserProfile.LIGHT
        else:
            user.type_of_theme = UserProfile.DARK
            user.save()
            request.session['theme'] = UserProfile.DARK
    else:
        if 'theme' in request.session:
            if request.session['theme'] == UserProfile.DARK:
                request.session['theme'] = UserProfile.LIGHT
            else:
                request.session['theme'] = UserProfile.DARK
        else:
            request.session['theme'] = UserProfile.LIGHT
    return redirect(request.META.get('HTTP_REFERER', '/'))


def login_view(request):
    if request.method == 'POST':
        username = request.POST['login']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            profile_id = User.objects.get(username=username).id
            profile = UserProfile.objects.filter(user_id=profile_id)
            if not profile:
                UserProfile(user_id=profile_id).save()
            if UserProfile.objects.get(user_id=profile_id).type_of_theme == UserProfile.DARK:
                request.session['theme'] = UserProfile.DARK
            else:
                request.session['theme'] = UserProfile.LIGHT
            return redirect(reverse('kinokino:main'))
        if not User.objects.filter(username=username):
            return render(request, 'kinokino/login.html', {'error_message': 'Такого логина не существует'})
        return render(request, 'kinokino/login.html', {'error_message': 'Неправильный пароль'})
    return render(request, 'kinokino/login.html')


def logout_view(request):
    logout(request)
    return redirect(reverse('kinokino:main'))


def registration(request):
    if request.method == 'POST':
        username = request.POST['login']
        if User.objects.filter(username=username):
            return render(request, 'kinokino/registration.html', {'error_message': 'Имя пользователя занято'})
        if request.POST['password'] != request.POST['repeat_password']:
            return render(request, 'kinokino/registration.html', {'error_message': 'Пароли не совпадают'})
        user = User.objects.create_user(username=username, password=request.POST['password'])
        UserProfile(user_id=user.id).save()
        login(request, user)
        return redirect(reverse('kinokino:main'))
    return render(request, 'kinokino/registration.html')


@require_POST
def searching(request):
    return redirect('kinokino:search', search_text=request.POST['search_text'])


def search(request, search_text):
    movie_data = Movie.objects.values_list('kinopoisk_id', flat=True)
    context = {
        'movie_data': movie_data,
        'name': search_text,
    }
    search_result = cache.get(f'search_result_{search_text}')
    if not search_result:
        search_result = search_function['search_film']([
            ('name', search_text)
        ])
        if search_result == 'всё плохо((((':
            return render(request, 'kinokino/search.html', {'seach_text': search_text, 'error_message': search_result})
        cache.set(f'search_result_{search_text}', search_result, 60*5)

    context['search_result'] = search_result
    return render(request, 'kinokino/search.html', context)


@require_POST
def add_movie(request):
    name = request.POST['movie_name']
    kinopoisk_id = int(request.POST['movie_id'])
    year = int(request.POST['movie_year'])
    movie_type = request.POST['movie_type']
    if request.POST['release_years']:
        all_episode_count = 0
        seasons = []
        search_result = search_function['search_series']([('movieId', kinopoisk_id)])
        release_year_start = request.POST['release_years'][11:15]
        release_year_end = request.POST['release_years'][24:28]
        new_movie = Movie.objects.create(
            name=name,
            kinopoisk_id=kinopoisk_id,
            year=year,
            seasons_count=len(search_result),
        )
        new_movie.type = movie_type
        if release_year_start != 'None':
            new_movie.release_year_start = release_year_start
        if release_year_end != 'None':
            new_movie.release_year_end = release_year_end
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
                if episodes_info['name']:
                    episode_name = episodes_info['name']
                else:
                    episode_name = episodes_info['enName']
                date_str = episodes_info['date'][:10]
                date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                Episode.objects.create(
                    number=number,
                    date=date,
                    name=episode_name,
                    season=new_season,
                )
        new_movie.episodes_count = all_episode_count
        new_movie.save()
    else:
        new_movie = Movie.objects.create(
            name=name,
            kinopoisk_id=kinopoisk_id,
            year=year,
        )
        new_movie.type = movie_type
        new_movie.save()
    return redirect('kinokino:search', search_text=request.POST['search_text'])


@login_required()
def favorite(request):
    user_info = UserProfile.objects.get(user_id=request.user.id)
    favorite_movies = user_info.movie_set.all()
    context = {
        'favorite_movies': favorite_movies,
    }
    return render(request, 'kinokino/favorite.html', context)


@login_required
@require_POST
def favorite_movie(request):
    user_info = UserProfile.objects.get(user_id=request.user.id)
    movie_details = Movie.objects.get(kinopoisk_id=request.POST['movie_id'])

    if request.POST['fav'] == 'rem':
        movie_details.favorite.remove(user_info)
    elif request.POST['fav'] == 'add':
        movie_details.favorite.add(user_info)

    return redirect(request.META.get('HTTP_REFERER', '/'))


def all_movies(request):
    movie_data = Movie.objects.all()
    context = {
        'movie_data': movie_data,
    }
    if request.user.is_authenticated:
        user = UserProfile.objects.get(user_id=request.user.id)
        favorite_movie_list = user.movie_set.values_list('kinopoisk_id', flat=True)
        context['favorite_movie_list'] = favorite_movie_list
    return render(request, 'kinokino/all_movies.html', context)


def all_seasons(request, movie_id):
    movie_data = Movie.objects.all()
    movie = Movie.objects.get(kinopoisk_id=movie_id)
    season_info = movie.season_set.all()
    context = {
        'movie_data': movie_data,
        'movie': movie,
        'season_info': season_info,
    }
    if request.user.is_authenticated:
        user = UserProfile.objects.get(user_id=request.user.id)
        favorite_movie_list = user.movie_set.values_list('kinopoisk_id', flat=True)
        context['favorite_movie_list'] = favorite_movie_list
    return render(request, 'kinokino/all_seasons.html', context)


def all_episodes(request, movie_id, season_id):
    movie_data = Movie.objects.all()
    movie = Movie.objects.get(kinopoisk_id=movie_id)
    season_info = movie.season_set.all()
    episodes = season_info.get(number=season_id).episode_set.all().order_by('number')
    context = {
        'movie_data': movie_data,
        'movie': movie,
        'season_info': season_info,
        'episodes': episodes,
    }
    if request.user.is_authenticated:
        user = UserProfile.objects.get(user_id=request.user.id)
        favorite_movie_list = user.movie_set.values_list('kinopoisk_id', flat=True)
        context['favorite_movie_list'] = favorite_movie_list
    return render(request, 'kinokino/all_episodes.html', context)


def main(request):
    context = {

    }
    return render(request, 'kinokino/main.html', context)
