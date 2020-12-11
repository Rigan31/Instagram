from django.shortcuts import render
from django.db import connection
from django.http import HttpResponse
from django.http import JsonResponse
from pages import views
import datetime

# Create your views here.

def timeToAge(sss):

    age = ""
    for i in range(0,len(sss),2):
        if int(sss[i]) != 0:
            if sss[i+1] == 'Y':
                if int(sss[i]) == 1: age = sss[i] + ' year ago'
                else: age = sss[i] + ' years ago'
            elif sss[i+1] == 'M':
                if int(sss[i]) == 1: age = sss[i] + ' month ago'
                else: age = sss[i] + ' months ago'
            elif sss[i+1] == 'D':
                if int(sss[i]) == 1: age = sss[i] + ' day ago'
                else: age = sss[i] + ' days ago'
            elif sss[i+1] == 'h':
               if int(sss[i]) == 1: age = sss[i] + ' hour ago'
               else: age = sss[i] + ' hours ago'
            elif sss[i+1] == 'm':
                 if int(sss[i]) == 1: age = sss[i] + ' minute ago'
                 else: age = sss[i] + ' minutes ago'
            elif sss[i+1] == 's':
                if int(sss[i]) == 1: age = sss[i] + ' second ago'
                else: age = sss[i] + ' seconds ago'
            break

    if age == "": age = '0 second ago'
    return age



def isLike(user_id, post_id):
    cursor = connection.cursor()
    sql = "SELECT COUNT(*) FROM LIKES WHERE USER_ID = %s AND CONTENT_ID = %s AND CONTENT_TYPE = 'PST';"
    cursor.execute(sql, [user_id, post_id])
    count = cursor.fetchone()
    cursor.close()

    if count[0] == 0:
        return False;
    else:
        return True;


def totalLikes(post_id):
    cursor = connection.cursor()
    sql = "SELECT COUNT(*) FROM LIKES WHERE CONTENT_ID = %s AND CONTENT_TYPE = 'PST';"
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



def getPost(user_id, post_id):

    photos = collectphotos(post_id)
    videos = collectVideos(post_id)

    if len(photos)>0: photos = photos[0]
    else: photos = ""
    if len(videos)>0: videos = videos[0]
    else: videos = ""

    data = {
        'user_id': user_id,
        'post_id': post_id,
        'photo': photos,
        'video': videos,
        'total_likes': views.totalLikes(post_id),
        'comment_count': views.getCommentCount(post_id, user_id),
    }
    return data


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
    

    sql = "SELECT LOCATION, AGE_OF_CONTENT(DATE_OF_STORY) FROM STORY WHERE USER_ID = %s ORDER BY DATE_OF_STORY DESC;"
    cursor.execute(sql, [user_id])
    result = cursor.fetchall()

    stories_info = []
    for r in result:
        sss = r[1].split()
        age = timeToAge(sss)
        row = {
            'story_path': r[0],
            'creation_time': age,
        }
        stories_info.append(row)
    
    
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
        'msg': msg,
        'stories_info': stories_info,
    }

    return context

def getUserPosts(user_id):
    cursor = connection.cursor()

    sql = "SELECT ID FROM POSTS WHERE USER_ID = %s ORDER BY CREATION_DATE DESC;"
    cursor.execute(sql, [user_id])
    rr = cursor.fetchall()

    posts = []
    for r in rr:
        posts.append(getPost(user_id, r[0]))

    return posts

def getUserSharedPosts(user_id):

    cursor = connection.cursor()
    sql = "SELECT ID, POST_ID FROM SHARE_POST WHERE USER_ID = %s ORDER BY DATE_OF_SHARE DESC;"
    cursor.execute(sql, [user_id])
    rr = cursor.fetchall()

    posts = []
    for r in rr:
        shared_id = r[0]
        shared_post_id = r[1]

        photos = collectphotos(shared_post_id)
        videos = collectVideos(shared_post_id)

        if len(photos) > 0: photos = photos[0]
        else: photos = ""

        if len(videos) > 0: videos = videos[0]
        else: videos = ""

        total_likes = views.totalLikes(shared_id, 'SHR')
        comment_count = views.getCommentCount(shared_id, user_id, 'SHR')

        row = {
            'shared_id': shared_id,
            'photo': photos,
            'video': videos,
            'total_likes': total_likes,
            'comment_count': comment_count,
        }
        posts.append(row)

    cursor.close()
    return posts



def profile(request, user_id):
    observer_id = request.session['user_id']

    context = {
        'base': base_profile(request, user_id, observer_id),
        'user_posts': getUserPosts(user_id),
        'shared_posts': getUserSharedPosts(user_id),
        'user_id': observer_id,
    }
    return render(request, 'user/user.html', context)


def getSavedPosts(user_id):
    cursor = connection.cursor()

    sql = "SELECT POST_ID FROM SAVED WHERE USER_ID = %s ORDER BY DATE_OF_SAVED DESC;"
    cursor.execute(sql, [user_id])
    rr = cursor.fetchall()

    posts = []
    for r in rr:
        posts.append(getPost(user_id, r[0]))

    return posts


def archive(request, user_id):
    observer_id = request.session['user_id']
    context = {
        'base': base_profile(request, user_id, observer_id),
        'user_posts': getSavedPosts(user_id),
        'user_id': observer_id,
    }
    return render(request, 'user/archive.html', context)


def isFollowee(user_id, searchee_id):
    cursor = connection.cursor()
    sql = "SELECT COUNT(*) FROM FOLLOW WHERE FOLLOWER_ID = %s AND FOLLOWEE_ID = %s;"
    cursor.execute(sql, [user_id, searchee_id])
    result = cursor.fetchone()
    cursor.close()

    if result[0] == 0:
        return False
    else:
        return True

def isFollower(user_id, searchee_id):
    cursor = connection.cursor()
    sql = "SELECT COUNT(*) FROM FOLLOW WHERE FOLLOWER_ID = %s AND FOLLOWEE_ID = %s;"
    cursor.execute(sql, [searchee_id, user_id])
    result = cursor.fetchone()
    cursor.close()

    if result[0] == 0:
        return False
    else:
        return True


def followee_count(user_id):
    cursor = connection.cursor()
    sql = "SELECT COUNT(FOLLOWEE_ID) FROM FOLLOW WHERE FOLLOWER_ID = %s;"
    cursor.execute(sql, [user_id])
    following = cursor.fetchone()
    following = following[0]

    cursor.close()
    return following

def follower_count(user_id):
    cursor = connection.cursor()
    sql = "SELECT COUNT(FOLLOWER_ID) FROM FOLLOW WHERE FOLLOWEE_ID = %s;"
    cursor.execute(sql, [user_id])
    following = cursor.fetchone()
    following = following[0]

    cursor.close()
    return following


def user_following(user_id, observer_id):
    if user_id == observer_id:
        cursor = connection.cursor()
        sql = "SELECT FOLLOWEE_ID FROM FOLLOW WHERE FOLLOWER_ID = %s;"
        cursor.execute(sql, [user_id])
        result = cursor.fetchall()
        
        following = []
        for r in result:
            sql = "SELECT NAME, PROFILE_PIC, USERNAME, FACEBOOK_LINK, TWITTER_LINK FROM USERDATA WHERE ID = %s;"
            cursor.execute(sql, [r[0]])
            info = cursor.fetchone()
            row = {
                'name': info[0],
                'profile_photo': info[1],
                'username': info[2],
                'fb_link': info[3],
                'tw_link': info[4],
                'follower_count': follower_count(r[0]),
                'followee_count': followee_count(r[0]),
                'isFollowee': isFollowee(user_id, r[0]),
                'isFollower': isFollower(user_id, r[0]),
                'id': r[0],
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
            sql = "SELECT NAME, PROFILE_PIC, USERNAME, FACEBOOK_LINK, TWITTER_LINK FROM USERDATA WHERE ID = %s;"
            cursor.execute(sql, [r[0]])
            info = cursor.fetchone()
            row = {
                'name': info[0],
                'profile_photo': info[1],
                'username': info[2],
                'fb_link': info[3],
                'tw_link': info[4],
                'follower_count': follower_count(r[0]),
                'followee_count': followee_count(r[0]),
                'isFollowee': isFollowee(user_id, r[0]),
                'isFollower': isFollower(user_id, r[0]),
                'id': r[0],
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
        'user_follower': user_follower(user_id, observer_id),
        'user_id': observer_id,
    }
    return render(request, 'user/follower.html', context)

def follow_button(request, user_id):
    print("hoy na kn")
    if request.is_ajax:
        user_id = request.POST['user_id']
        followee_id = request.POST['followee_id']
        msg = request.POST['msg']

        cursor = connection.cursor()
        newMsg = ""

        if msg == 'Unfollow':
            sql = "DELETE FROM FOLLOW WHERE FOLLOWER_ID = %s AND FOLLOWEE_ID = %s;"
            cursor.execute(sql, [user_id, followee_id])

            sql = "SELECT COUNT(*) FROM FOLLOW WHERE FOLLOWER_ID =%s AND FOLLOWEE_ID = %s;"
            cursor.execute(sql, [followee_id, user_id])
            result = cursor.fetchone()
            if result[0] == 0:
                newMsg = "Follow"
            else:
                newMsg = "Follow back"
        else:
            sql = "INSERT INTO FOLLOW VALUES(%s, %s);"
            cursor.execute(sql, [user_id, followee_id])
            newMsg = "Unfollow"
        
        return JsonResponse({'newMsg': newMsg})
