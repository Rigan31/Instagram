from django.shortcuts import render
from django.db import connection
from django.http import HttpResponse

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




def base_profile(request, user_id, observer_id):
    cursor = connection.cursor()

    sql = "SELECT COUNT(*) FROM FOLLOW WHERE FOLLOWER_ID = %s AND FOLLOWEE_ID = %s;"
    cursor.execute(sql, [observer_id, user_id])       
    result = cursor.fetchone()
    
    if result[0] == 0:
        msg = "Follow"
    else:
        msg = "Unfollow"

    if request.method == 'POST':
        
        if msg == "Follow" :
            sql = "INSERT INTO FOLLOW VALUES(%s, %s);"
            cursor.execute(sql, [observer_id, user_id])
            msg = "Unfollow"
        else:
            sql = "DELETE FROM FOLLOW WHERE FOLLOWER_ID = %s AND FOLLOWEE_ID = %s;"
            cursor.execute(sql, [observer_id, user_id])
            msg = "Follow"

    sql = "SELECT PROFILE_PIC, USERNAME, NAME, FACEBOOK_LINK, TWITTER_LINK FROM USERDATA WHERE ID= %s;"
    cursor.execute(sql, [user_id])
    profile_information = cursor.fetchone()

    if len(profile_information) == 0:
        return HttpResponse("This person is not available.")

    sql = "SELECT COUNT(*) FROM POSTS WHERE USER_ID = %s;"
    cursor.execute(sql, [user_id])
    post_count = cursor.fetchone()
    post_count = post_count[0]

    sql = "SELECT COUNT(FOLLOWEE_ID) FROM FOLLOW WHERE FOLLOWER_ID = %s;"
    cursor.execute(sql, [user_id])
    following = cursor.fetchone()
    following = following[0]

    sql = "SELECT COUNT(FOLLOWER_ID) FROM FOLLOW WHERE FOLLOWEE_ID = %s;"
    cursor.execute(sql, [user_id])
    follower = cursor.fetchone()
    follower = follower[0]
    
    cursor.close()

    


    context = {
        'profile_pic': profile_information[0],
        'username': profile_information[1],
        'name': profile_information[2],
        'facebook_link': profile_information[3],
        'twitter_link': profile_information[4],
        'post_count': post_count,
        'following': following,
        'follower': follower,
        'observee_id': user_id,
        'msg': msg
    }

    return context

def getUserPosts(user_id):
    cursor = connection.cursor()

    sql = "SELECT * FROM POSTS WHERE USER_ID = %s ORDER BY CREATION_DATE DESC;"
    cursor.execute(sql, [user_id])
    result = cursor.fetchall()

    posts = []

    for r in result:
        post_id = r[0]
        creation_time = r[1]
        caption = r[2]
        update_time = r[3]
        visibility = r[4]
        poster_id = r[5]

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
    
    return posts


def profile(request, user_id):
    observer_id = request.session['user_id']
    context = {
        'base': base_profile(request, user_id, observer_id),
        'user_posts': getUserPosts(user_id),
        'user_id': observer_id,
    }
    return render(request, 'user/user.html', context)

def user_following(user_id, observer_id):
    if user_id == observer_id:
        cursor = connection.cursor()
        sql = "SELECT FOLLOWEE_ID FROM FOLLOW WHERE FOLLOWER_ID = %s;"
        cursor.execute(sql, [user_id])
        result = cursor.fetchall()
        
        following = []
        for r in result:
            sql = "SELECT NAME, PROFILE_PIC FROM USERDATA WHERE ID = %s;"
            cursor.execute(sql, [r[0]])
            info = cursor.fetchone()
            row = {
                'name': info[0],
                'profile_photo': info[1],
            }
            following.append(row)
        cursor.close()
        return following


def user_follower(user_id, observer_id):
    if user_id == observer_id:
        cursor = connection.cursor()
        sql = "SELECT FOLLOWER_ID FROM FOLLOW WHERE FOLLOWEE_ID = %s;"
        cursor.execute(sql, [user_id])
        result = cursor.fetchall()
        
        follower = []
        for r in result:
            sql = "SELECT NAME, PROFILE_PIC FROM USERDATA WHERE ID = %s;"
            cursor.execute(sql, [r[0]])
            info = cursor.fetchone()
            row = {
                'name': info[0],
                'profile_photo': info[1],
            }
            follower.append(row)
        cursor.close()
        return follower


def following(request, user_id):
    observer_id = request.session['user_id']
    context = {
        'base': base_profile(request, user_id, observer_id),
        'user_following': user_following(user_id, observer_id),
        'user_id': observer_id,
    }
    return render(request, 'user/following.html', context)

def follower(request, user_id):
    observer_id = request.session['user_id']
    context = {
        'base': base_profile(request, user_id, observer_id),
        'user_following': user_follower(user_id, observer_id),
        'user_id': observer_id,
    }
    return render(request, 'user/following.html', context)