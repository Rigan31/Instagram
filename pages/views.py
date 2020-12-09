from django.shortcuts import render, redirect
from django.db import connection
from django.core.files.storage import FileSystemStorage
from django.db.models.functions.datetime import datetime
from django.http import JsonResponse
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


def getStories(user_id):
    cursor = connection.cursor()
    sql = "SELECT * FROM STORY WHERE (USER_ID = %s OR USER_ID = ANY(SELECT FOLLOWEE_ID FROM FOLLOW WHERE FOLLOWER_ID = %s)) AND TRUNC(SYSDATE-DATE_OF_STORY) < 1 ORDER BY DATE_OF_STORY DESC;"
    cursor.execute(sql, [user_id, user_id])
    all_stories = cursor.fetchall()

    stories = []

    for story in all_stories:
        story_id = story[0]
        story_path = story[1]
        creation_time = story[2]
        storier_id = story[3]

        sql = "SELECT NAME, PROFILE_PIC FROM USERDATA WHERE ID = %s;"
        cursor.execute(sql, [storier_id])
        storier_info = cursor.fetchone()
        storier_name = storier_info[0]
        storier_photo = storier_info[1]

        row = {
            'story_path': story_path,
            'creatoin_time': creation_time,
            'storier_id': storier_id,
            'storier_name': storier_name,
            'storier_photo': storier_photo,
        }
        stories.append(row)

    return stories

def getPosts(user_id):
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

def index(request):
    if 'user_id' not in request.session:
        return redirect('login')
    user_id = request.session['user_id']
    cursor = connection.cursor()
    sql = "SELECT PROFILE_PIC, NAME FROM USERDATA WHERE ID =%s;"
    cursor.execute(sql, [user_id])
    user_info = cursor.fetchone()
    cursor.close()

    context = {
        'posts': getPosts(user_id),
        'stories': getStories(user_id),
        'user_id': user_id,
        'user_photo': user_info[0],
        'name': user_info[1],
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

def searchUsers(user_id, value):
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
        sql = "SELECT MESSAGE, DATE_OF_MESSAGE FROM NOTIFICATION WHERE USER_ID =%s ORDER BY DATE_OF_MESSAGE DESC;"
        cursor.execute(sql, [user_id])
        result = cursor.fetchall()

        notifications = []

        for r in result:
            date = r[1]
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
                'action-id': action_id,
                'action_name': action_name,
                'action_photo': action_photo,
                'msg': msg,
                'date': date,
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
    return age

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
            'reply_text': reply_text,
        }
        data.append(reply)

    cursor.close()
    return data

def getComment(post_id, logged_user_id):

    cursor = connection.cursor()
    sql = "SELECT ID, TEXT, AGE_OF_CONTENT(DATE_OF_COMMENT), POST_ID, USER_ID, CONTENT_TYPE FROM COMMENTS WHERE POST_ID = %s AND CONTENT_TYPE = 'PST' ORDER BY DATE_OF_COMMENT;"
    cursor.execute(sql,[post_id])
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

def getPost(user_id, post_id):

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

    isfollower = isFollowee(user_id, poster_id)
    isfollowee = isFollowee(user_id, poster_id)

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
        'total_likes': totalLikes(post_id),
        'isLike': isLike(user_id, post_id),
        'isSave': isSave(user_id, post_id),
        'age': age,
        'isFollower': isfollower,
        'isFollowee': isfollowee,
        'comments': getComment(post_id, user_id),
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
        creation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor = connection.cursor()
        sql = "INSERT INTO COMMENTS(TEXT, DATE_OF_COMMENT, POST_ID, USER_ID, CONTENT_TYPE) VALUES(%s, %s, %s, %s, 'PST');"
        cursor.execute(sql,[comment, creation_time, post_id, commenter])

        sql = "SELECT ID FROM COMMENTS WHERE USER_ID = %s AND DATE_OF_COMMENT LIKE %s;"
        cursor.execute(sql, [commenter, creation_time])
        comment_id = cursor.fetchone()[0]
        comment_age = "1 second ago"

        sql = "SELECT USERNAME, PROFILE_PIC FROM USERDATA WHERE ID = %s;"
        cursor.execute(sql, [commenter])
        r = cursor.fetchone()

        commenter_username = r[0]
        commenter_id = commenter
        commenter_photo = r[1]

        data = {
            'comment_id': comment_id,
            'comment_age': comment_age,
            'commenter_id': commenter_id,
            'commenter_username': commenter_username,
            'commenter_photo': commenter_photo,
            'is_like': False,
            'like_count': 0,
            'comment_text': comment,
        }
        cursor.close()
        return JsonResponse(data)

def addReply(request):
    if request.is_ajax:
        replier_id = request.POST['replier']
        comment_id = request.POST['comment_id']
        reply_text = request.POST['reply']
        creation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor = connection.cursor()
        sql = "INSERT INTO COMMENT_REPLY(USER_ID, TEXT, COMMENT_ID, COMMENT_TIME) VALUES(%s, %s, %s, %s);"
        cursor.execute(sql, [replier_id, reply_text, comment_id, creation_time])

        sql = "SELECT ID FROM COMMENT_REPLY WHERE USER_ID = %s AND COMMENT_TIME LIKE %s;"
        cursor.execute(sql, [replier_id, creation_time])
        reply_id = cursor.fetchone()[0]

        reply_age = "1 second ago"
        is_like = False
        like_count = 0

        sql = "SELECT USERNAME, PROFILE_PIC FROM USERDATA WHERE ID=%s;"
        cursor.execute(sql, [replier_id])
        r = cursor.fetchone()

        replier_username = r[0]
        replier_photo = r[1]

        data = {
            'reply_id': reply_id,
            'reply_age': reply_age,
            'replier_id': replier_id,
            'replier_username': replier_username,
            'replier_photo': replier_photo,
            'is_like': is_like,
            'like_count': like_count,
            'reply_text': reply_text,
            'comment_id': comment_id,
        }
        cursor.close()
        return JsonResponse(data)
