from django.shortcuts import render
from django.db import connection
from django.http import HttpResponse

# Create your views here.

def profile(request, user_id):
    cursor = connection.cursor()
    observer_id = request.session['user_id']

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
        'observer_id': observer_id,
        'user_id': user_id,
        'msg': msg
    }

    return render(request, 'user/user.html', context)