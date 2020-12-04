from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('edit-profile', views.edit_profile, name='edit-profile'),
    path('search-history', views.search_history, name='search-history'),
    path('search-delete', views.search_delete, name='search-delete'),
    path('change-profile-photo', views.change_profile_photo, name='change-profile-photo')
]