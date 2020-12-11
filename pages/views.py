from django.shortcuts import render, redirect
from django.db import connection
from django.core.files.storage import FileSystemStorage
from django.db.models.functions.datetime import datetime
from django.http import JsonResponse
from collections import Counter

import os

# Create your views here.

def isLike(user_id, post_id, content_type="PST"):
    cursor = connection.cursor()
    sql = "SELECT COUNT(*) FROM LIKES WHERE USER_ID = %s AND CONTENT_ID = %s AND CONTENT_TYPE = %s;"
    cursor.execute(sql, [user_id, post_id, content_type])
    count = cursor.fetchone()
    cursor.close()

    if count[0] == 0:
        return False;
    else:
        return True;

def totalLikes(post_id, content_type="PST"):
    cursor = connection.cursor()
    sql = "SELECT COUNT(*) FROM LIKES WHERE CONTENT_ID = %s AND CONTENT_TYPE = %s;"
    cursor.execute(sql, [post_id, content_type])
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


##### new stories code


def getEachUserStories(storier_id):
    cursor = connection.cursor()
    sql = "SELECT LOCATION, AGE_OF_CONTENT(DATE_OF_STORY) FROM STORY WHERE USER_ID = %s AND TRUNC(SYSDATE-DATE_OF_STORY) < 1 ORDER BY DATE_OF_STORY DESC;"
    cursor.execute(sql, [storier_id])
    result = cursor.fetchall()

    if len(result) == 0:
        return 

    stories_info = []
    for story in result:
        sss = story[1].split()
        age = timeToAge(sss)
        row = {
            'story_path': story[0],
            'creation_time': age,
        }
        stories_info.append(row)
    
    return stories_info



def getStories(user_id):
    cursor = connection.cursor()
    
    stories_user_list = []
    stories_user_list.append(user_id)
    sql = "SELECT FOLLOWEE_ID FROM FOLLOW WHERE FOLLOWER_ID = %s;"
    cursor.execute(sql, [user_id])

    result = cursor.fetchall()

    for r in result:
        stories_user_list.append(r[0])
    
    stories = []
    for storier_id in stories_user_list:
        stories_info = getEachUserStories(storier_id)
        if stories_info:
            sql = "SELECT NAME, PROFILE_PIC FROM USERDATA WHERE ID = %s;"
            cursor.execute(sql, [storier_id])
            storier_info = cursor.fetchone()
            storier_name = storier_info[0]
            storier_photo = storier_info[1]

            story_row = {
                'storier_id': storier_id,
                'storier_name': storier_name,
                'storier_photo': storier_photo,
                'stories_info': stories_info,
                'mediaCount': stories_info.__len__(),
            }
            stories.append(story_row)
    
    return stories










def getPosts1(user_id):
    cursor = connection.cursor()

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


def getPosts(user_id):
    user_list = []
    user_list.append(user_id)

    cursor = connection.cursor()
    sql = "SELECT FOLLOWEE_ID FROM FOLLOW WHERE FOLLOWER_ID = %s;"
    cursor.execute(sql, [user_id])
    result = cursor.fetchall()

    for r in result:
        user_list.append(r[0])
    
    posts = []
    for user in user_list:
        sql = "SELECT ID FROM POSTS WHERE USER_ID = %s;"
        cursor.execute(sql, [user])
        result = cursor.fetchall()
        for r in result:
            posts.append(getPost(user, r[0]))
    

    posts = sorted(posts, key=lambda k: k['creation_time'], reverse=True) 
    return posts


def getSuggestions(user_id):
    cursor = connection.cursor()
    sql = "SELECT FOLLOWEE_ID FROM FOLLOW WHERE FOLLOWER_ID = %s;"
    cursor.execute(sql, [user_id])

    result = cursor.fetchall()

    suggestions_list = []
    for r in result:
        sql = "SELECT FOLLOWEE_ID FROM FOLLOW WHERE FOLLOWER_ID = %s AND FOLLOWEE_ID <> %s;"
        cursor.execute(sql, [r[0], user_id])
        result2 = cursor.fetchall()
        for r2 in result2:
            if isFollowee(user_id, r2[0]):
                continue
            suggestions_list.append(r2[0])
    
    suggestions = sorted(set(suggestions_list), key = lambda ele: suggestions_list.count(ele), reverse=True)
    
    print(suggestions)
    sugges = []

    for s in suggestions:
        sql = "SELECT NAME, PROFILE_PIC, USERNAME, FACEBOOK_LINK, TWITTER_LINK FROM USERDATA WHERE ID = %s;"
        cursor.execute(sql, [s])
        result = cursor.fetchone()
        row = {
            'sugges_name': result[0],
            'sugges_photo': result[1],
            'sugges_username': result[2],
            'sugges_fb': result[3],
            'sugges_tw': result[4],
            'sugges_id': s,
            'sugges_follower': follower_count(s),
            'sugges_followee': followee_count(s),
            'isFollower': isFollower(user_id, s),
        }
        sugges.append(row)
    cursor.close()
    
    print(sugges)
    return sugges


######################## new code for suggestions page
    
def suggestions(request):
    user_id = request.session['user_id']
    context = {
        'suggestions': getSuggestions(user_id),
        'user_id': user_id,
    }
    return render(request, 'pages/suggestions.html', context)



def index(request):
    if 'user_id' not in request.session:
        return redirect('login')
    user_id = request.session['user_id']
    cursor = connection.cursor()
    sql = "SELECT PROFILE_PIC, NAME, USERNAME FROM USERDATA WHERE ID =%s;"
    cursor.execute(sql, [user_id])
    user_info = cursor.fetchone()
    cursor.close()

    suggestions = getSuggestions(user_id)

    if len(suggestions) > 5:
        suggestions = suggestions[:5]

    context = {
        'posts': getPosts(user_id),
        'stories': getStories(user_id),
        'user_id': user_id,
        'user_photo': user_info[0],
        'name': user_info[1],
        'username': user_info[2],
        'suggestions': suggestions,
    }
    
    return render(request, 'pages/index.html', context)
    
def create_post(request):
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

        return redirect('index')
        
    sql = "SELECT NAME, PROFILE_PIC FROM USERDATA WHERE ID = %s;"
    cursor.execute(sql, [user_id])
    poster = cursor.fetchone()
    cursor.close()        

    context = {
        'user_id':user_id,
        'name': poster[0],
        'photo': poster[1]
    }

    return render(request, 'pages/create-post.html', context)

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
        content_id = request.POST['content_id']
        content_type = request.POST['content_type']

        cursor = connection.cursor()

        if isLike(user_id, content_id, content_type):
            sql = "DELETE FROM LIKES WHERE USER_ID = %s AND CONTENT_ID = %s AND CONTENT_TYPE = %s;"
            cursor.execute(sql, [user_id, content_id, content_type])
        else:
            sql = "INSERT INTO LIKES(USER_ID, CONTENT_ID, CONTENT_TYPE) VALUES(%s,%s,%s);"
            cursor.execute(sql, [user_id, content_id, content_type])
        
        cursor.close()
        return JsonResponse({'count': totalLikes(content_id, content_type)})

def saved(request):
    if request.is_ajax:
        user_id = request.POST['user_id']
        post_id = request.POST['post_id']

        cursor = connection.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        p = isSave(user_id, post_id)

        if isSave(user_id, post_id):
            sql = "DELETE FROM SAVED WHERE USER_ID = %s AND POST_ID = %s;"
            cursor.execute(sql, [user_id, post_id])
        else:
            sql = "INSERT INTO SAVED(USER_ID, POST_ID, DATE_OF_SAVED) VALUES(%s,%s,%s);"
            cursor.execute(sql, [user_id, post_id, timestamp])
        
        cursor.close()
        return JsonResponse({})



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

def searchUsers(user_id, value):
    cursor = connection.cursor()
    value = value.lower()
    almostValue = '%'+value+'%'

    sql = "SELECT ID, NAME, PROFILE_PIC, USERNAME, FACEBOOK_LINK, TWITTER_LINK FROM USERDATA WHERE LOWER(NAME) LIKE %s OR LOWER(USERNAME) LIKE %s;"
    cursor.execute(sql, [almostValue, almostValue])
    result = cursor.fetchall()
    cursor.close()

    search_users = []
    for r in result:
        row = {
            'searchee_id': r[0],
            'searchee_name': r[1],
            'searchee_photo': r[2],
            'searchee_username': r[3],
            'searchee_follower': follower_count(r[0]),
            'searchee_followee': followee_count(r[0]),
            'searchee_fb': r[4],
            'searchee_tw': r[5],
            'isFollowee': isFollowee(user_id, r[0]),
            'isFollower': isFollower(user_id, r[0]),
        }
        search_users.append(row)
    
    return search_users

def searchPosts(user_id, value): 
    cursor = connection.cursor()
    value = value[1:]
    value = value.lower()
    almostValue = '%'+value+'%'
            
    sql = "SELECT * FROM POSTS WHERE ID = ANY(SELECT POST_ID FROM POST_TAG WHERE TAG_ID = ANY(SELECT ID FROM TAGS WHERE LOWER(TAG_NAME) LIKE %s)) ORDER BY CREATION_DATE DESC;"
    cursor.execute(sql, [almostValue])
    result = cursor.fetchall()

    print(result)
            
    search_posts = []
    for r in result:
        post_id = r[0]
        print(r[0])
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
        search_posts.append(row)
    
    return search_posts

def search(request):
    user_id = request.session['user_id']
    if request.method == 'GET':
        value = request.GET['search']

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = connection.cursor()
        sql = "INSERT INTO SEARCH(NAME, DATE_OF_SEARCH, USER_ID) VALUES(%s, %s, %s);"
        cursor.execute(sql, [value, timestamp, user_id])
        cursor.close()

        search_users = []
        search_posts = []

        if value[0] == '#':
            search_posts = searchPosts(user_id, value)
        else:
            search_users = searchUsers(user_id, value)

        context = {
            'search_posts': search_posts,
            'search_users': search_users,
            'user_id': user_id,
        }

        return render(request, 'pages/search.html', context)
               
def follow(request):
    if request.is_ajax:
        user_id = request.POST['user_id']
        followee_id = request.POST['followee_id']
        msg = request.POST['msg']
        print('adfjalksjdflajdsfljdflasdjflaksdjflka')

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

######################################################
#asif code ......................
#My change 1 showing liked user list
def like_list(request):
    if request.is_ajax:

        logged_user_id = request.GET['logged_user']
        content_id = request.GET['content_id']
        content_type = request.GET['content_type']

        cursor = connection.cursor()
        sql = "SELECT * FROM USERDATA WHERE ID = ANY(SELECT USER_ID FROM LIKES WHERE CONTENT_ID = %s AND CONTENT_TYPE = %s);"
        cursor.execute(sql,[content_id, content_type])

        users = []
        result = cursor.fetchall()

        for r in result:
            user_id = r[0]
            user_username = r[3]
            user_name = r[4]
            user_img = r[6]
            user_link = "user/" + str(user_id)

            row = {
                'user_id': user_id,
                'username': user_username,
                'user_img': user_img,
                'user_link': user_link,
                'user_name': user_name,
                'isFollowee': isFollowee(logged_user_id, user_id),
                'isFollower': isFollower(logged_user_id, user_id),
            }
            users.append(row)
        cursor.close()

        context ={
            'liked_user_list': users,
            'logged_user_id': logged_user_id,
        }
        return JsonResponse(context)

#############################################

def notification(request):
    user_id = request.session['user_id']
    if request.is_ajax:
        cursor = connection.cursor()
        sql = "SELECT MESSAGE, AGE_OF_CONTENT(DATE_OF_MESSAGE) FROM NOTIFICATION WHERE USER_ID =%s ORDER BY DATE_OF_MESSAGE DESC;"
        cursor.execute(sql, [user_id])
        result = cursor.fetchall()

        notifications = []

        for r in result:
            date = r[1]
            sss = date.split()
            age = timeToAge(sss)
            
            msg = r[0].split(",")
            action_id = msg[0]
            msg = msg[1]

            sql = "SELECT NAME, PROFILE_PIC FROM USERDATA WHERE ID = %s;"
            cursor.execute(sql, [action_id])
            action= cursor.fetchone()
            action_name = action[0]
            action_photo = action[1]

            msg = action_name+' '+msg
            print(msg)
            row = {
                'action_id': action_id,
                'action_name': action_name,
                'action_photo': action_photo,
                'msg': msg,
                'date': age,
            }
            notifications.append(row)
        
        cursor.close()
        context = {
            'notifications': notifications,
            'user_id': user_id,
        }
        return JsonResponse(context)


################# my new code for chat

def searchChatUsersList(value):
    cursor = connection.cursor()
    value = value.lower()
    almostValue = '%'+value+'%'

    sql = "SELECT ID, NAME, PROFILE_PIC FROM USERDATA WHERE LOWER(NAME) LIKE %s OR LOWER(USERNAME) LIKE %s;"
    cursor.execute(sql, [almostValue, almostValue])
    result = cursor.fetchall()
    cursor.close()

    search_users = []
    for r in result:
        row = {
            'searchee_id': r[0],
            'searchee_name': r[1],
            'searchee_photo': r[2],
        }
        search_users.append(row)
    
    return search_users


def searchUserChat(request):
    if request.is_ajax:
        value = request.GET['value']
        return JsonResponse({'chatUserList': searchChatUsersList(value)})

def lastChatUser(user_id):
    cursor = connection.cursor()
    sql = "SELECT USER_TO_ID, MAX(DATE_OF_MESSAGE) FROM USER_CHAT WHERE USER_FROM_ID = %s GROUP BY (USER_TO_ID) UNION SELECT USER_FROM_ID, MAX(DATE_OF_MESSAGE) FROM USER_CHAT WHERE USER_TO_ID = %s GROUP BY (USER_FROM_ID);"
    cursor.execute(sql, [user_id, user_id])
    result = cursor.fetchall()
    result = sorted(result, key=lambda tup: tup[1], reverse=True)

    visited = set() 
  
    Output = [] 
   
    for a, b in result: 
        if not a in visited: 
            visited.add(a) 
            Output.append((a, b))

    ans = []
    for r in Output:
        sql = "SELECT NAME, USERNAME, PROFILE_PIC FROM USERDATA WHERE ID = %s;"
        cursor.execute(sql, [r[0]])
        result = cursor.fetchone()

        row = {
            'partner_id': r[0], 
            'partner_name': result[0],
            'partner_username': result[1],
            'partner_profile_pic': result[2],
        }
        ans.append(row)

    return ans


def chat(request):
    user_id = request.session['user_id']

    context = {
        'user_id': user_id,
        'last_chat_user': lastChatUser(user_id),
    }
    return render(request, 'pages/chat.html', context)


def chat_to_partner(request, partner_id):
    user_id = request.session['user_id']
    cursor = connection.cursor()
    sql = "SELECT MESSAGE, DATE_OF_MESSAGE, USER_FROM_ID FROM USER_CHAT WHERE (USER_FROM_ID = %s AND USER_TO_ID = %s) OR (USER_FROM_ID = %s AND USER_TO_ID = %s) ORDER BY DATE_OF_MESSAGE ASC;"
    cursor.execute(sql, [user_id, partner_id, partner_id, user_id])
    result = cursor.fetchall()

    sql = "SELECT NAME, PROFILE_PIC FROM USERDATA WHERE ID = %s;"
    cursor.execute(sql, [partner_id])
    info = cursor.fetchone()

    messages = []

    for r in result:
        msg = r[0]
        msg_date = r[1]
        user_from_id = r[2]

        row = {
            'msg': msg,
            'msg_date': msg_date,
            'user_from_id': user_from_id,
        }

        messages.append(row)

    context = {
        'user_id': user_id,
        'partner_id': partner_id,
        'messages': messages,
        'last_chat_user': lastChatUser(user_id),
        'partner_name': info[0],
        'partner_photo': info[1],
    }

    return render(request, 'pages/user-to-user-chat.html', context)

def send_msg_to_partner(request):
    user_id = request.session['user_id']
    if request.is_ajax:
        msg = request.GET['msg']
        partner_id = request.GET['partner_id']
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor = connection.cursor()
        sql = "INSERT INTO USER_CHAT VALUES(%s, %s, %s, %s);"
        cursor.execute(sql, [user_id, partner_id, msg, timestamp])
        
        context = {
            'msg': msg,
            'msg_date': timestamp,
        }
        return JsonResponse(context)


###################### FOR POST

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

def addLinkToText(text):

    text = str(text)

    if text[0] != '@': return (text, -1, '')

    k = 0
    for i in range(1,len(text),1):
        if text[i] == ' ':
            k = i
            break
    username = text[1:k]
    cursor = connection.cursor()
    sql = "SELECT ID FROM USERDATA WHERE USERNAME = %s;"
    cursor.execute(sql, [username])

    try: id = cursor.fetchone()[0]
    except: return (text, -1, '')

    text = text[k:]
    return (text, id, username)

def getReply(comment_id, logged_user_id):

    cursor = connection.cursor()
    sql = "SELECT ID, USER_ID, TEXT, COMMENT_ID, AGE_OF_CONTENT(COMMENT_TIME) FROM COMMENT_REPLY WHERE COMMENT_ID = %s ORDER BY COMMENT_TIME;"
    cursor.execute(sql, [comment_id])
    r = cursor.fetchall()

    data = []

    for row in r:
        reply_id = row[0]
        replier_id = row[1]
        reply_text = row[2]
        comment_id = row[3]
        reply_age = timeToAge(row[4].split())

        (reply_text_without_link, replied_to, replied_to_username) = addLinkToText(reply_text)

        sql = "SELECT USERNAME, PROFILE_PIC FROM USERDATA WHERE ID = %s;"
        cursor.execute(sql, [replier_id])
        rr = cursor.fetchone()

        replier_username = rr[0]
        replier_photo = rr[1]
        is_like = isLike(logged_user_id, reply_id, 'RPL')
        like_count = totalLikes(reply_id, 'RPL')

        reply = {
            'reply_id': reply_id,
            'reply_age': reply_age,
            'replier_id': replier_id,
            'replier_username': replier_username,
            'replier_photo': replier_photo,
            'is_like': is_like,
            'like_count': like_count,
            'reply_text': reply_text_without_link,
            'replied_to': replied_to,
            'replied_to_username': replied_to_username,
        }
        data.append(reply)

    cursor.close()
    return data

def getComment(post_id, logged_user_id, content_type = 'PST'):

    cursor = connection.cursor()
    sql = "SELECT ID, TEXT, AGE_OF_CONTENT(DATE_OF_COMMENT), POST_ID, USER_ID, CONTENT_TYPE FROM COMMENTS WHERE POST_ID = %s AND CONTENT_TYPE = %s ORDER BY DATE_OF_COMMENT;"
    cursor.execute(sql,[post_id, content_type])
    r = cursor.fetchall()

    data = []
    for row in r:

        comment_id = row[0]
        comment_text = row[1]
        comment_age = timeToAge(row[2].split())
        commenter_id = row[4]

        sql = "SELECT NAME, USERNAME, PROFILE_PIC FROM USERDATA WHERE ID = %s;"
        cursor.execute(sql,[commenter_id])
        rr = cursor.fetchone()

        commenter_username = rr[1]
        commenter_photo = rr[2]
        commenter_name = rr[0]
        comment_like_count = totalLikes(comment_id, 'CMNT')
        comment_is_like = isLike(logged_user_id, comment_id, 'CMNT')

        comment = {
            'comment_id': comment_id,
            'comment_text': comment_text,
            'comment_age': comment_age,
            'commenter_id': commenter_id,
            'commenter_username': commenter_username,
            'commenter_photo': commenter_photo,
            'comment_is_like': comment_is_like,
            'comment_like_count': comment_like_count,
            'commenter_name': commenter_name,
            'replies': getReply(comment_id, logged_user_id)
        }
        data.append(comment)

    cursor.close()
    return data


def getCommentCount(post_id, user_id, content_type = 'PST'):

    cursor = connection.cursor()
    sql = "SELECT ID FROM COMMENTS WHERE POST_ID = %s AND CONTENT_TYPE = %s;"
    cursor.execute(sql,[post_id, content_type])
    rr = cursor.fetchall()

    count = 0
    for r in rr:
        count = count + 1
        comment_id = r[0]

        sql = "SELECT COUNT(*) FROM COMMENT_REPLY WHERE COMMENT_ID = %s;"
        cursor.execute(sql, [comment_id])

        count += cursor.fetchone()[0]

    return count


def getPost(user_id, post_id, content_type='PST', sharer_id=0, shared_id=0):

    cursor = connection.cursor()
    sql = "SELECT USERNAME FROM USERDATA WHERE ID = %s;"
    cursor.execute(sql, [user_id])
    r = cursor.fetchone()

    username = r[0]

    sql = "SELECT * FROM POSTS WHERE ID=%s;"
    cursor.execute(sql, [post_id])
    r = cursor.fetchone()

    creation_time = r[1]
    caption = str(r[2])
    update_time = r[3]
    visibility = r[4]
    poster_id = r[5]

    photos = collectphotos(post_id)
    videos = collectVideos(post_id)

    sql = "SELECT NAME, PROFILE_PIC, USERNAME FROM USERDATA WHERE ID = %s;"
    cursor.execute(sql, [poster_id])
    poster_info = cursor.fetchone()
    poster_name = poster_info[0]
    poster_photo = poster_info[1]
    poster_username = poster_info[2]

    age = 0
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sql = "SELECT AGE_OF_CONTENT(CREATION_DATE) FROM POSTS WHERE ID=%s;"
    cursor.execute(sql,[post_id])
    sss = cursor.fetchone()[0].split()
    age = timeToAge(sss)

    if caption == 'None':
        caption = ""

    if str(update_time) == "None":
        update_time = creation_time

    if str(visibility) == "None":
        visibility = True

    if content_type == 'PST':
        isfollower = isFollower(user_id, poster_id)
        isfollowee = isFollowee(user_id, poster_id)
        total_likes = totalLikes(post_id)
        is_like = isLike(user_id, post_id)
        is_save = isSave(user_id, post_id)
        comments = getComment(post_id, user_id)
        comment_count = getCommentCount(post_id, user_id)
    else:
        isfollower = isFollower(user_id, sharer_id)
        isfollowee = isFollowee(user_id, sharer_id)
        total_likes = totalLikes(shared_id, 'SHR')
        is_like = isLike(user_id, shared_id, 'SHR')
        is_save = isSave(user_id, post_id)
        comments = getComment(shared_id, user_id, 'SHR')
        comment_count = getCommentCount(shared_id, user_id, 'SHR')

    data = {
        'user_id': user_id,
        'username': username,
        'post_id': post_id,
        'age': age,
        'creation_time': creation_time,
        'caption': caption,
        'update_time': update_time,
        'visibility': visibility,
        'photos': photos,
        'videos': videos,
        'poster_id': poster_id,
        'poster_name': poster_name,
        'poster_photo': poster_photo,
        'poster_username': poster_username,
        'total_likes': total_likes,
        'isLike': is_like,
        'isSave': is_save,
        'age': age,
        'isFollower': isfollower,
        'isFollowee': isfollowee,
        'comments': comments,
        'comment_count': comment_count,
        'mediaCount': range(1,photos.__len__() + videos.__len__() + 1,1),
    }
    cursor.close()
    return data


def post(request, post_id):

    if 'user_id' not in request.session:
        return redirect('login')
    user_id = request.session['user_id']

    return render(request, 'pages/post.html', getPost(user_id, post_id))

def addComment(request):

    if request.is_ajax:
        commenter = request.POST['commenter']
        post_id = request.POST['post_id']
        comment = request.POST['comment']
        content_type = request.POST['content_type']
        creation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(commenter, post_id, comment, content_type, creation_time)

        cursor = connection.cursor()
        sql = "INSERT INTO COMMENTS(TEXT, DATE_OF_COMMENT, POST_ID, USER_ID, CONTENT_TYPE) VALUES(%s, %s, %s, %s, %s);"
        cursor.execute(sql, [comment, creation_time, post_id, commenter, content_type])
        cursor.close()

        return JsonResponse({})


def addReply(request):
    if request.is_ajax:
        replier_id = request.POST['replier']
        comment_id = request.POST['comment_id']
        reply_text = request.POST['reply']
        creation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor = connection.cursor()
        sql = "INSERT INTO COMMENT_REPLY(USER_ID, TEXT, COMMENT_ID, COMMENT_TIME) VALUES(%s, %s, %s, %s);"
        cursor.execute(sql, [replier_id, reply_text, comment_id, creation_time])
        cursor.close()

        return JsonResponse({})


### 10-12-2020
######################################################
def editCaption(post_id, cap, post_type = 'PST'):

    cursor = connection.cursor()

    if post_type == 'PST':
        sql = 'UPDATE POSTS SET CAPTION = %s WHERE ID = %s;'
        cursor.execute(sql, [cap, post_id])
    elif post_type == 'SHR':
        sql = 'UPDATE SHARE_POST SET CAPTION = %s WHERE ID = %s;'
        cursor.execute(sql, [cap, post_id])

    cursor.close()



def deleteReply(reply_id):

    cursor = connection.cursor()

    sql = "DELETE FROM LIKES WHERE CONTENT_ID = %s AND CONTENT_TYPE = 'RPL';"
    cursor.execute(sql, [reply_id])

    sql = 'DELETE FROM COMMENT_REPLY WHERE ID = %s;'
    cursor.execute(sql, [reply_id])

    cursor.close()

def deleteComment(comment_id):

    cursor = connection.cursor()
    sql = "SELECT ID FROM COMMENT_REPLY WHERE COMMENT_ID = %s;"
    cursor.execute(sql, [comment_id])
    r = cursor.fetchall()

    for rr in r: deleteReply(rr[0])

    sql = "DELETE FROM LIKES WHERE CONTENT_ID = %s AND CONTENT_TYPE = 'CMNT';"
    cursor.execute(sql, [comment_id])

    sql = 'DELETE FROM COMMENTS WHERE ID = %s;'
    cursor.execute(sql, [comment_id])

    cursor.close()

def deletePost(post_id, content_type):

    cursor = connection.cursor()
    sql = "SELECT ID FROM COMMENTS WHERE POST_ID = %s AND CONTENT_TYPE = %s;"
    cursor.execute(sql, [post_id, content_type])
    r = cursor.fetchall()

    for rr in r: deleteComment(rr[0])

    if content_type == 'PST':

        sql = "DELETE FROM PHOTOS WHERE POST_ID = %s;"
        cursor.execute(sql, [post_id])

        sql = "DELETE FROM VIDEOS WHERE POST_ID = %s;"
        cursor.execute(sql, [post_id])

        sql = "DELETE FROM SAVED WHERE POST_ID = %s;"
        cursor.execute(sql, [post_id])

    sql = "DELETE FROM LIKES WHERE CONTENT_ID = %s AND CONTENT_TYPE = %s;"
    cursor.execute(sql, [post_id, content_type])

    if content_type == 'PST':
        sql = "DELETE FROM POSTS WHERE ID = %s;"
        cursor.execute(sql, [post_id])
    elif content_type == 'SHR':
        sql = "DELETE FROM SHARE_POST WHERE ID = %s;"
        cursor.execute(sql, [post_id])

    cursor.close()



def deleteContent(request):
    if request.is_ajax:

        content_id = request.POST['content_id']
        content_type = request.POST['content_type']
        content_in_content_type = request.POST['content_in_content_type']

        if content_type == 'CAP':
            if content_in_content_type == 'SHR': editCaption(content_id, '', content_in_content_type)
            else: editCaption(content_id, '')
        elif content_type == 'RPL': deleteReply(content_id)
        elif content_type == 'CMNT': deleteComment(content_id)
        elif content_type == 'PST' or content_type == 'SHR':
            deletePost(content_id, content_type)

        return JsonResponse({})



def changeCaption(request):
    if request.is_ajax:

        text = request.POST['text']
        post_id = request.POST['post_id']
        post_type = request.POST['post_type']

        editCaption(post_id, text, post_type)
        if post_type=='PST': addTag(text, post_id)
        return JsonResponse({})




################ my changes in view
def addCommentIndex(request):
    print("kasjdfljasldfjalsfasdfjlaskdfkasssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss")
    if request.is_ajax:
        commenter = request.POST['commenter']
        post_id = request.POST['post_id']
        comment = request.POST['comment']
        creation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("commenter", commenter)

        cursor = connection.cursor()
        sql = "INSERT INTO COMMENTS(TEXT, DATE_OF_COMMENT, POST_ID, USER_ID, CONTENT_TYPE) VALUES(%s, %s, %s, %s, 'PST');"
        cursor.execute(sql,[comment, creation_time, post_id, commenter])

        sql = "SELECT ID FROM COMMENTS WHERE TO_CHAR(TEXT) = %s AND DATE_OF_COMMENT = %s AND POST_ID = %s AND USER_ID = %s AND CONTENT_TYPE = 'PST';"
        cursor.execute(sql, [comment, creation_time, post_id, commenter])
        comment_id = cursor.fetchone()
        comment_id = comment_id[0]

        sql = "SELECT USERNAME FROM USERDATA WHERE ID = %s;"
        cursor.execute(sql, [commenter])
        username = cursor.fetchone()
        username = username[0]

        print(username, "fafadsfsdsssssssssssssssssssssssss ")
        print(comment_id)

        context = {
            'username': username,
            'comment_id': comment_id,
        }
        cursor.close()
        return JsonResponse(context)

#############################################
def sharePost(request):

    post_id = request.POST['post_id']
    user_id = request.POST['user_id']
    caption = request.POST['caption']
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor = connection.cursor()
    sql = "INSERT INTO SHARE_POST(USER_ID, POST_ID, CAPTION, DATE_OF_SHARE) VALUES(%s, %s, %s, %s);"
    cursor.execute(sql,[user_id, post_id, caption, time])

    sql = "SELECT ID FROM SHARE_POST WHERE USER_ID = %s AND POST_ID = %s AND DATE_OF_SHARE LIKE %s;"
    cursor.execute(sql, [user_id, post_id, time])
    r = cursor.fetchone()

    return JsonResponse({'id': r[0]})

def sharedPost(request, shared_id):

    if 'user_id' not in request.session:
        return redirect('login')
    user_id = request.session['user_id']

    cursor = connection.cursor()
    sql = "SELECT POST_ID, USER_ID, CAPTION, AGE_OF_CONTENT(DATE_OF_SHARE) FROM SHARE_POST WHERE ID = %s;"
    cursor.execute(sql, [shared_id])
    r = cursor.fetchone()

    sharer_id = r[1]
    post_id = r[0]
    age = timeToAge(r[3].split())
    caption = r[2]

    if str(caption) == "None": caption = ""

    sql = "SELECT USERNAME, PROFILE_PIC, NAME FROM USERDATA WHERE ID = %s"
    cursor.execute(sql, [sharer_id])
    r = cursor.fetchone()

    name = r[2]
    sharer_username = r[0]
    sharer_profile = r[1]
    post = getPost(user_id, post_id, 'SHR', sharer_id, shared_id)

    data = {
        'user_id': user_id,
        'shared_id': shared_id,
        'sharer_id': sharer_id,
        'sharer_name': name,
        'sharer_username': sharer_username,
        'sharer_profile': sharer_profile,
        'shared_age': age,
        'shared_caption': caption,
        'post': post,
    }
    return render(request, 'pages/share.html', data)

