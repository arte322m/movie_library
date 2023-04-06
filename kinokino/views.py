import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.parsers import JSONParser
from rest_framework.decorators import permission_classes
from rest_framework import status, permissions
from rest_framework.views import Request, APIView, Response

from kinokino.kinopoisk_parser import search_function, search_film_by_name
from kinokino.models import UserProfile, Movie, Episode, Season, MovieStatus, Collection, CompletedEpisode
from kinokino.serializers import MovieSerializer, UserSerializer, SearchingApiSerializer, AddMovieSerializer, \
    UserMoviesSerializer
from kinokino.utils import add_movie_episodes


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
        cache.set(f'search_result_{search_text}', search_result, 60 * 5)

    context['search_result'] = search_result
    return render(request, 'kinokino/search.html', context)


@require_POST
@login_required(login_url='/accounts/login')
def add_movie(request):
    if request.POST['release_years']:
        year_end = 0
        if request.POST['release_years'][23:27] != 'None':
            year_end = int(request.POST['release_years'][23:27])
        year_start = int(request.POST['release_years'][10:14])
    else:
        year_start = 0
        year_end = 0
    add_movie_episodes(
        username=request.user.username,
        name=request.POST['movie_name'],
        kin_id=int(request.POST['movie_id']),
        year=int(request.POST['movie_year']),
        movie_type=request.POST['movie_type'],
        preview_url=request.POST['preview_url'],
        year_start=year_start,
        year_end=year_end,
    )
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
    completed = False
    completed_episodes_count = 0
    for season in movie.season_set.all():
        completed_episodes_count += season.completedepisode_set.count()
    if MovieStatus.objects.filter(movie=movie, status='Просмотрено'):
        completed = True
    context = {
        'movie': movie,
        'completed': completed,
        'statuses': statuses,
        'season_info': season_info,
        'favorite_movie_list': favorite_movie_list,
        'completed_episodes_count': completed_episodes_count,
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
    completed = False
    if MovieStatus.objects.filter(movie=movie, status='Просмотрено'):
        completed = True
    if request.method == 'POST':
        if request.POST['add_or_rem'] == '+':
            episode = Episode.objects.get(id=request.POST['episode'])
            CompletedEpisode.objects.create(user=user, season=season_info, episode=episode)
        elif request.POST['add_or_rem'] == '-':
            episode = Episode.objects.get(id=request.POST['episode'])
            CompletedEpisode.objects.get(user=user, season=season_info, episode=episode).delete()
        return redirect(request.META.get('HTTP_REFERER', '/'))
    context = {
        'season_episodes': season_episodes,
        'completed': completed,
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
    user_movies = user.moviestatus_set.all()
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


@csrf_exempt
def movie_list_api(request):
    if request.method == 'GET':
        movies = Movie.objects.all()
        serializer = MovieSerializer(movies, many=True)
        return JsonResponse(serializer.data, safe=False)

    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = MovieSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def movie_detail_api(request, pk):
    try:
        movie = Movie.objects.get(pk=pk)
    except Movie.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = MovieSerializer(movie)
        return JsonResponse(serializer.data)

    if request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = MovieSerializer(movie, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    if request.method == 'DELETE':
        movie.delete()
        return HttpResponse(status=204)


class CreateUserApi(APIView):

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.data['username']
            try:
                User.objects.get(username=username)
            except User.DoesNotExist:
                user = User.objects.create(username=username, password=make_password(username))
                UserProfile.objects.create(user=user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SearchingApi(APIView):

    # permission_classes = []

    def get(self, request: Request):
        serializer = SearchingApiSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        film_name = data['name']

        search_film_by_name_result = cache.get(f'search_result_{film_name}')
        if not search_film_by_name_result:
            search_film_by_name_result = search_film_by_name(film_name)
            if search_film_by_name_result == 'всё плохо((((':
                return Response(status=status.HTTP_403_FORBIDDEN)
            cache.set(f'search_result_{film_name}', search_film_by_name_result, 60 * 5)

        return Response(data=search_film_by_name_result, status=status.HTTP_200_OK)


class AddMovieApi(APIView):

    def post(self, request: Request):

        serializer = AddMovieSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        search_text = data['name']
        search_film_by_name_result = cache.get(f'search_result_{search_text}')
        if not search_film_by_name_result:
            search_film_by_name_result = search_film_by_name(search_text)
            if search_film_by_name_result == 'всё плохо((((':
                return Response(status=status.HTTP_403_FORBIDDEN)
            cache.set(f'search_result_{search_text}', search_film_by_name_result, 60 * 5)

        film_number = int(data['number'])
        found_film = search_film_by_name_result[film_number]
        username = data['username']
        name = found_film['name']
        kin_id = found_film['id']
        year = found_film['year']
        movie_type = found_film['type']
        preview_url = found_film['poster']['previewUrl']
        try:
            release_years = found_film['releaseYears']
        except KeyError:
            year_start = 0
            year_end = 0
        else:
            year_start = release_years[0]['start']
            year_end = release_years[0]['end']

        return add_movie_episodes(
            username=username,
            name=name,
            kin_id=kin_id,
            year=year,
            movie_type=movie_type,
            preview_url=preview_url,
            year_start=year_start,
            year_end=year_end,
        )


class ProfileStatisticsApi(APIView):

    def post(self, request: Request):
        serializer = UserSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        username = data['username']
        try:
            user = UserProfile.objects.get(user__username=username)
        except UserProfile.DoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        all_count = user.moviestatus_set.all().count()
        planned_count = user.moviestatus_set.filter(status=MovieStatus.PLANNED_TO_WATCH).count()
        completed_count = user.moviestatus_set.filter(status=MovieStatus.COMPLETED).count()
        watching_count = user.moviestatus_set.filter(status=MovieStatus.WATCHING).count()
        result = {
            'all_count': all_count,
            'planned_count': planned_count,
            'completed_count': completed_count,
            'watching_count': watching_count,
        }
        return Response(data=result, status=status.HTTP_200_OK)


class UserMovieApi(APIView):

    def post(self, request: Request):
        serializer = UserMoviesSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        username = data['username']
        try:
            user = UserProfile.objects.get(user__username=username)
        except UserProfile.DoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        field_name = data['field_name']
        if not field_name == 'None':
            result_data = user.moviestatus_set.filter(status=field_name).values_list(
                'movie__name',
                'movie__year',
                'movie__release_year_start',
                'movie__release_year_end',
            )
        else:
            result_data = user.moviestatus_set.all().values_list(
                'movie__name',
                'movie__year',
                'movie__release_year_start',
                'movie__release_year_end',
            )
        result_data_list = []
        for film_info in result_data:
            result_data_list.append(
                {
                    'name': film_info[0],
                    'year': film_info[1],
                    'year_start': film_info[2],
                    'year_end': film_info[3],
                }
            )
        result_data_json = {'films': result_data_list}
        return Response(data=result_data_json, status=status.HTTP_200_OK)
