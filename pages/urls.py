from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('create-post', views.create_post, name='create-post'),
    path('likes', views.likes, name='likes'),
    path('saved', views.saved, name='saved'),
    path('create-story', views.create_story, name='create-story'),
    path('search', views.search, name='search'),
    path('follow', views.follow, name='follow'),
    path('like_list', views.like_list, name='like_list'),
]