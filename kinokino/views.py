import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from kinokino.kinopoisk_api_search import search_function
from kinokino.models import UserProfile, Movie, Episode, Season, MovieStatus, Collection, CompletedEpisode


@login_required(login_url='/accounts/login')
def main(request):
    return render(request, 'kinokino/main.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['login']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            profile_id = User.objects.get(username=username).id
            u_profile = UserProfile.objects.filter(user_id=profile_id)
            if not u_profile:
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


@login_required(login_url='/accounts/login')
def logout_view(request):
    logout(request)
    return redirect(reverse('kinokino:main'))


@login_required(login_url='/accounts/login')
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


@require_POST
@login_required(login_url='/accounts/login')
def searching(request):
    return redirect('kinokino:search', search_text=request.POST['search_text'])


@login_required(login_url='/accounts/login')
def search(request, search_text):
    user = UserProfile.objects.get(user_id=request.user.id)
    movie_data = user.moviestatus_set.values_list('movie__kinopoisk_id', flat=True)
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
@login_required(login_url='/accounts/login')
def add_movie(request):
    user = UserProfile.objects.get(user_id=request.user.id)
    kinopoisk_id = int(request.POST['movie_id'])
    if Movie.objects.filter(kinopoisk_id=kinopoisk_id):
        movie = Movie.objects.get(kinopoisk_id=kinopoisk_id)
        MovieStatus.objects.create(movie=movie, user=user, status=MovieStatus.PLANNED_TO_WATCH)
        return redirect('kinokino:search', search_text=request.POST['search_text'])
    name = request.POST['movie_name']
    year = int(request.POST['movie_year'])
    movie_type = request.POST['movie_type']
    preview_url = request.POST['preview_url']
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
            preview_url=preview_url,
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
    MovieStatus.objects.create(movie=new_movie, user=user, status=MovieStatus.PLANNED_TO_WATCH)
    return redirect('kinokino:search', search_text=request.POST['search_text'])


@require_POST
@login_required(login_url='/accounts/login')
def add_movie_to_favorite(request):
    user_info = UserProfile.objects.get(user_id=request.user.id)
    movie_details = Movie.objects.get(kinopoisk_id=request.POST['movie_id'])

    if request.POST['fav'] == 'rem':
        movie_details.favorite.remove(user_info)
    elif request.POST['fav'] == 'add':
        movie_details.favorite.add(user_info)

    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='/accounts/login')
def bookmarks(request):
    return render(request, 'kinokino/bookmarks.html')


@login_required(login_url='/accounts/login')
def bookmarks_favorite(request):
    user_info = UserProfile.objects.get(user_id=request.user.id)
    favorite_movies = user_info.movie_set.all()
    context = {
        'favorite_movies': favorite_movies,
    }
    return render(request, 'kinokino/bookmarks_favorite.html', context)


@login_required(login_url='/accounts/login')
def bookmarks_watching(request):
    user = UserProfile.objects.get(user_id=request.user.id)
    movie_list = user.moviestatus_set.filter(status='Смотрю').values_list('movie__name', flat=True)
    context = {
        'movie_list': movie_list,
    }
    return render(request, 'kinokino/bookmarks_watching.html', context)


@login_required(login_url='/accounts/login')
def bookmarks_planned_to_watch(request):
    user = UserProfile.objects.get(user_id=request.user.id)
    movie_list = user.moviestatus_set.filter(status='Запланировано').values_list('movie__name', flat=True)
    context = {
        'movie_list': movie_list,
    }
    return render(request, 'kinokino/bookmarks_planned_to_watch.html', context)


@login_required(login_url='/accounts/login')
def bookmarks_completed(request):
    context = {}
    user = UserProfile.objects.get(user_id=request.user.id)
    movie_list = user.moviestatus_set.filter(status='Просмотрено').values_list('movie__name', flat=True)
    context['movie_list'] = movie_list
    return render(request, 'kinokino/completed_bookmarks.html', context)


@login_required(login_url='/accounts/login')
def bookmarks_all(request):
    user = UserProfile.objects.get(user_id=request.user.id)
    favorite_movie_list = user.movie_set.values_list('kinopoisk_id', flat=True)
    movie_data = user.moviestatus_set.all()
    context = {
        'movie_data': movie_data,
        'favorite_movie_list': favorite_movie_list,
    }
    return render(request, 'kinokino/bookmarks_all.html', context)


@login_required(login_url='/accounts/login')
def detail_movie(request, movie_id):
    user = UserProfile.objects.get(user_id=request.user.id)
    favorite_movie_list = user.movie_set.values_list('kinopoisk_id', flat=True)
    movie = Movie.objects.get(kinopoisk_id=movie_id)
    season_info = movie.season_set.order_by('number').all()
    statuses = MovieStatus.MOVIE_STATUS
    context = {
        'movie': movie,
        'statuses': statuses,
        'season_info': season_info,
        'favorite_movie_list': favorite_movie_list,
    }
    if MovieStatus.objects.filter(user=user, movie=movie):
        movie_status = MovieStatus.objects.get(user=user, movie=movie)
        context['movie_status'] = movie_status
    return render(request, 'kinokino/detail_movie.html', context)


@login_required(login_url='/accounts/login')
def detail_season(request, movie_id, season_id):
    movie = Movie.objects.get(kinopoisk_id=movie_id)
    season_info = movie.season_set.get(number=season_id)
    season_episodes = season_info.episode_set.all().order_by('number')
    user = UserProfile.objects.get(user_id=request.user.id)
    user_complete_episodes = user.completedepisode_set.filter(season=season_info).values_list('episode_id', flat=True)
    if request.method == 'POST':
        if request.POST['add_or_rem'] == '+':
            episode = Episode.objects.get(id=request.POST['episode'])
            CompletedEpisode.objects.create(user=user, season=season_info, episode=episode)
            return redirect(request.META.get('HTTP_REFERER', '/'))
        elif request.POST['add_or_rem'] == '-':
            episode = Episode.objects.get(id=request.POST['episode'])
            CompletedEpisode.objects.get(user=user, season=season_info, episode=episode).delete()
            return redirect(request.META.get('HTTP_REFERER', '/'))
    context = {
        'season_episodes': season_episodes,
        'movie_id': movie_id,
        'user_complete_episodes': user_complete_episodes,
    }
    return render(request, 'kinokino/detail_season.html', context)


@require_POST
@login_required(login_url='/accounts/login')
def add_status(request):
    movie = Movie.objects.get(id=request.POST['movie_id'])
    user = UserProfile.objects.get(user_id=request.user.id)
    statuses = {
        'Смотрю': MovieStatus.WATCHING,
        'Запланировано': MovieStatus.PLANNED_TO_WATCH,
        'Просмотрено': MovieStatus.COMPLETED,
    }
    status = statuses[request.POST['status']]
    if not MovieStatus.objects.filter(movie=movie, user=user):
        MovieStatus.objects.create(movie=movie, user=user, status=status)
    else:
        new_status = MovieStatus.objects.get(movie=movie, user=user)
        new_status.status = status
        new_status.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))


@require_POST
@login_required(login_url='/accounts/login')
def delete_status(request):
    movie = Movie.objects.get(id=request.POST['movie_id'])
    user = UserProfile.objects.get(user_id=request.user.id)
    MovieStatus.objects.get(movie=movie, user=user).delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='/accounts/login')
def collections(request):
    user = UserProfile.objects.get(user_id=request.user.id)
    user_collections = user.collection_set.all()
    context = {
        'all_collections': user_collections,
    }
    return render(request, 'kinokino/collections.html', context)


@login_required(login_url='/accounts/login')
def create_collection(request):
    if request.method == 'POST':
        Collection.objects.create(name=request.POST['name'], user=UserProfile.objects.get(user_id=request.user.id))
        return redirect('kinokino:collections')
    return render(request, 'kinokino/create_collection.html')


@login_required(login_url='/accounts/login')
def collection_detail(request, collection_id):
    detail = Collection.objects.get(id=collection_id)
    movies_set = detail.movie.all()
    context = {
        'detail': detail,
        'movies_set': movies_set,
    }
    return render(request, 'kinokino/collection_detail.html', context)


@login_required(login_url='/accounts/login')
def change_collection(request, collection_id):
    user = UserProfile.objects.get(user_id=request.user.id)
    user_movies = user.movie_set.all()
    collection = Collection.objects.get(id=collection_id)
    movies_in_collection = collection.movie.all()
    context = {
        'user_movies': user_movies,
        'movies_in_collection': movies_in_collection,
        'collection_id': collection_id,
    }
    return render(request, 'kinokino/change_collection.html', context)


@require_POST
@login_required(login_url='/accounts/login')
def add_movie_in_collection(request):
    collection = Collection.objects.get(id=request.POST['collection_id'])
    movie_details = Movie.objects.get(id=request.POST['movie_id'])

    if request.POST['fav'] == 'rem':
        collection.movie.remove(movie_details)
    elif request.POST['fav'] == 'add':
        collection.movie.add(movie_details)
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='/accounts/login')
def profile(request):
    user = UserProfile.objects.get(user_id=request.user.id)
    planned_to_watch_count = user.moviestatus_set.filter(status=MovieStatus.PLANNED_TO_WATCH).count
    complete_count = user.moviestatus_set.filter(status=MovieStatus.COMPLETED).count
    watching_count = user.moviestatus_set.filter(status=MovieStatus.WATCHING).count
    context = {
        'watching_count': watching_count,
        'complete_count': complete_count,
        'planned_to_watch_count': planned_to_watch_count,
    }
    return render(request, 'kinokino/profile.html', context)
