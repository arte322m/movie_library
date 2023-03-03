from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.cache import cache
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


@require_POST
def searching(request):
    return redirect('kinokino:search', search_text=request.POST['search_text'])


def search(request, search_text):
    context = {
        'name': search_text,
    }
    search_result = cache.get(f'search_result_{search_text}')
    if not search_result:
        search_result = search_function['search_film']([('field', 'name'), ('search', search_text)])
        cache.set(f'search_result_{search_text}', search_result, 60*5)
    context['search_result'] = search_result
    return render(request, 'kinokino/search.html', context)


@require_POST
def add_movie(request):
    return redirect('kinokino:search', search_text=request.POST['search_text'])


def main(request):
    context = {

    }
    return render(request, 'kinokino/main.html', context)
