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
    path('notification', views.notification, name='notification'),


    path('chat', views.chat, name='chat'),
    path('search-chat-user', views.searchUserChat, name='search-chat-user'),
    path('send-msg-to-partner', views.send_msg_to_partner, name='send-msg-to-partner'),
    path('chat-to-partner/<int:partner_id>', views.chat_to_partner, name='chat-to-partner'),



    path('post/<int:post_id>', views.post, name='post'),
    path('addComment', views.addComment, name='addComment'),
    path('addReply', views.addReply, name='addReply'),


    path('deleteContent', views.deleteContent, name='deleteContent'),
    path('changeCaption', views.changeCaption, name='changeCaption'),



    path('suggestions', views.suggestions, name='suggestions'),
]