from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from kinokino.kinopoisk_api_search import search_function
from kinokino.models import UserProfile


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


def base_search(request):
    return render(request, 'kinokino/search_page.html')


@require_POST
def searching(request):
    film_params = []
    if request.POST['search_text']:
        film_name = f"f_{request.POST['search_text']}"
        film_params.append(film_name)
    if request.POST['genre'] and request.POST['genre'] != 'Все жанры':
        film_genre = f'g_{request.POST["genre"]}'
        film_params.append(film_genre)
    params = '__'.join(film_params)

    return redirect('kinokino:search', search_text=params)


def search(request, search_text):

    context = {}
    params_kinopoisk = []

    params_dict = {
        'f_': 'search_text',
        'g_': 'genre',
        'r_': 'rating',
        'y_': 'year',
    }
    params_dict_reverse = {
        'search_text': 'name',
        'genre': 'genres.name',
        'rating': 'rating.kp',
        'year': 'year',
    }

    for text in search_text.split('__'):
        param = text[:2]
        new_param = params_dict[param]
        if param == 'g_':
            context.setdefault(new_param, [])
            context[new_param].append(text[2:])
            params_kinopoisk.append(('field', params_dict_reverse[new_param]))
            params_kinopoisk.append(('search', text[2:]))
        else:
            params_kinopoisk.append(('field', params_dict_reverse[new_param]))
            params_kinopoisk.append(('search', text[2:]))
        context.setdefault(new_param, text[2:])
    search_function['search_film'](params_kinopoisk)
    return render(request, 'kinokino/search.html', context)


def main(request):
    context = {

    }
    return render(request, 'kinokino/main.html', context)
