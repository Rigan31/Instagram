from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('post', views.post, name='post'),
    path('likes', views.likes, name='likes'),
    path('saved', views.saved, name='saved'),
    path('create-story', views.create_story, name='create-story')
]