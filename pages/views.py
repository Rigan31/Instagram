from django.shortcuts import render, redirect
from django.db import connection
from django.core.files.storage import FileSystemStorage
from django.db.models.functions.datetime import datetime
from django.http import JsonResponse
import os

# Create your views here.

def isLike(user_id, post_id):
    cursor = connection.cursor()
    sql = "SELECT COUNT(*) FROM LIKES WHERE USER_ID = %s AND POST_ID = %s;"
    cursor.execute(sql, [user_id, post_id])
    count = cursor.fetchone()
    cursor.close()

    if count[0] == 0:
        return False;
    else:
        return True;


def totalLikes(post_id):
    cursor = connection.cursor()
    sql = "SELECT COUNT(*) FROM LIKES WHERE POST_ID = %s;"
    cursor.execute(sql, [post_id])
    total_likes = cursor.fetchone()
    return total_likes[0]


def isSave(user_id, post_id):
    cursor = connection.cursor()
    sql = "SELECT COUNT(*) FROM SAVED WHERE USER_ID = %s AND POST_ID = %s;"
    cursor.execute(sql, [user_id, post_id])
    count = cursor.fetchone()
    cursor.close()

    if count[0] == 0:
        return False;
    else:
        return True;


def addTag(caption, post_id):
    hashtag_list = []
    for word in caption.split():
        if word[0] == '#':
            hashtag_list.append(word[1:])
    
    hashtag_list = list(dict.fromkeys(hashtag_list))
    
    cursor = connection.cursor()
    for hashtag in hashtag_list:
        sql = "SELECT ID FROM TAGS WHERE TAG_NAME = %s;"
        cursor.execute(sql, [hashtag])
        hashtag_id = cursor.fetchone()

        if hashtag_id:
            continue
        
        sql = "INSERT INTO TAGS(TAG_NAME) VALUES(%s);"
        cursor.execute(sql, [hashtag])

        sql = "SELECT ID FROM TAGS WHERE TAG_NAME = %s;"
        cursor.execute(sql, [hashtag])
        hashtag_id = cursor.fetchone()
        hashtag_id = hashtag_id[0]
        
        sql = "INSERT INTO POST_TAG(TAG_ID, POST_ID) VALUES(%s, %s);"
        cursor.execute(sql, [hashtag_id, post_id])
    cursor.close()


def collectphotos(post_id):
    cursor = connection.cursor()
    sql = "SELECT PHOTO_PATH FROM PHOTOS WHERE POST_ID = %s;"
    cursor.execute(sql, [post_id])
    photos_path = cursor.fetchall()

    photos = []
    for photo_path in photos_path:
        photos.append(photo_path[0])
    return photos


def collectVideos(post_id):
    cursor = connection.cursor()
    sql = "SELECT VIDEO_PATH FROM VIDEOS WHERE POST_ID = %s;"
    cursor.execute(sql, [post_id])
    videos_path = cursor.fetchall()

    videos = []
    for video_path in videos_path:
        videos.append(video_path[0])
    return videos


def index(request):
    if 'user_id' not in request.session:
        return redirect('login')
    user_id = request.session['user_id']
    cursor = connection.cursor()

    ####################### Story #####################
    sql = "SELECT * FROM STORY WHERE (USER_ID = %s OR USER_ID = ANY(SELECT FOLLOWEE_ID FROM FOLLOW WHERE FOLLOWER_ID = %s)) AND TRUNC(SYSDATE-DATE_OF_STORY) < 1 ORDER BY DATE_OF_STORY DESC;"
    cursor.execute(sql, [user_id, user_id])
    all_stories = cursor.fetchall()

    ###################################################
    sql = "SELECT * FROM POSTS WHERE USER_ID = %s OR USER_ID = ANY (SELECT FOLLOWEE_ID FROM FOLLOW WHERE FOLLOWER_ID = %s) ORDER BY CREATION_DATE DESC;"
    cursor.execute(sql, [user_id, user_id])
    result = cursor.fetchall()

    posts = []

    for r in result:
        post_id = r[0]
        creation_time = r[1]
        caption = r[2]
        update_time = r[3]
        visibility = r[4]
        poster_id = r[5]

        cursor = connection.cursor()
        sql = "SELECT NAME, PROFILE_PIC FROM USERDATA WHERE ID = %s;"
        cursor.execute(sql, [poster_id])
        poster_info = cursor.fetchone()
        poster_name = poster_info[0]
        poster_photo = poster_info[1]

        row = { 
                'creation_time': creation_time,
                'caption': caption,
                'update_time': update_time,
                'poster_name': poster_name,
                'poster_photo': poster_photo,
                'photos': collectphotos(post_id),
                'post_id': post_id,
                'poster_id': poster_id,
                'total_likes': totalLikes(post_id),
                'isLike': isLike(user_id, post_id),
                'isSave': isSave(user_id, post_id),
                'videos': collectVideos(post_id),
            }
        posts.append(row)

    context = {
        'posts': posts,
        'user_id': user_id,
    }

    return render(request, 'pages/index.html', context)
    

def post(request):
    img_extension = [".jpg", ".jpeg", ".png"]
    video_extension = [".mp4", ".avi", ".mov", ".webm", ".mkv", ".gif"]
    user_id = request.session['user_id']

    cursor = connection.cursor()

    if request.method == "POST":
        caption = request.POST['caption']
        
        

        print("user id: ", user_id)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(timestamp)

        print(user_id)
        sql = "INSERT INTO POSTS(CREATION_DATE, CAPTION, USER_ID) VALUES(%s, %s, %s);"
        cursor.execute(sql, [timestamp, caption, user_id])

        sql = "SELECT ID FROM POSTS WHERE USER_ID = %s AND CREATION_DATE LIKE %s;"
        cursor.execute(sql, [user_id, timestamp])
        result = cursor.fetchone()
        post_id = result[0]

        addTag(caption, post_id)

        files = request.FILES.getlist('file')
        for file in files:
            fs = FileSystemStorage()
            file_new_path = fs.save(file.name, file)
            root, extention = os.path.splitext(file.name)
            file_url = fs.url(file_new_path)

            if extention in img_extension:
                sql = "INSERT INTO PHOTOS(PHOTO_PATH, POST_ID) VALUES(%s, %s);"
                cursor.execute(sql, [file_url, post_id])
            elif extention in video_extension:
                sql = "INSERT INTO VIDEOS(VIDEO_PATH, POST_ID) VALUES(%s, %s);"
                cursor.execute(sql, [file_url, post_id])

    sql = "SELECT NAME, PROFILE_PIC FROM USERDATA WHERE ID = %s;"
    cursor.execute(sql, [user_id])
    poster = cursor.fetchone()
    cursor.close()        

    context = {
        'user_id':user_id,
        'name': poster[0],
        'photo': poster[1]
    }

    return render(request, 'pages/post.html', context)


def create_story(request):
    user_id = request.session['user_id']
    cursor = connection.cursor()

    if request.method == 'POST':
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file = request.FILES['file']
        fs = FileSystemStorage()
        file_new_path = fs.save(file.name, file)
        root, extention = os.path.splitext(file.name)            
        file_url = fs.url(file_new_path)

        sql = "INSERT INTO STORY(LOCATION, DATE_OF_STORY, USER_ID) VALUES(%s, %s, %s);"
        cursor.execute(sql, [file_url, timestamp, user_id])
        cursor.close()
        return redirect('index')
    
    context = {
        'user_id': user_id,
    }
    return render(request, 'pages/create-story.html', context)

def likes(request):
    if request.is_ajax:
        user_id = request.POST['user_id']
        post_id = request.POST['post_id']

        print(user_id, post_id)
        cursor = connection.cursor()

        if isLike(user_id, post_id):
            sql = "DELETE FROM LIKES WHERE USER_ID = %s AND POST_ID = %s;"
            cursor.execute(sql, [user_id, post_id])
        else:
            sql = "INSERT INTO LIKES VALUES(%s,%s);"
            cursor.execute(sql, [user_id, post_id])
        
        cursor.close()
        return JsonResponse({'count': totalLikes(post_id)})


def saved(request):
    if request.is_ajax:
        user_id = request.POST['user_id']
        post_id = request.POST['post_id']

        print(user_id, post_id)
        cursor = connection.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if isSave(user_id, post_id):
            sql = "DELETE FROM SAVED WHERE USER_ID = %s AND POST_ID = %s;"
            cursor.execute(sql, [user_id, post_id])
        else:
            sql = "INSERT INTO SAVED(USER_ID, POST_ID, DATE_OF_SAVED) VALUES(%s,%s,%s);"
            cursor.execute(sql, [user_id, post_id, timestamp])
        
        cursor.close()
        return JsonResponse({})
        
