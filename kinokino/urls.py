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
]
