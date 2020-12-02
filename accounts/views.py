from django.shortcuts import render, redirect
from django.db import connection
from django.core.files.storage import FileSystemStorage
from django.db.models.functions.datetime import datetime
from django.contrib.staticfiles.storage import staticfiles_storage

# Create your views here.

def register(request):
    if request.method == 'POST':
        email = request.POST['email']
        name = request.POST['name']
        username = request.POST['username']
        password = request.POST['password']
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor = connection.cursor()
        sql = "SELECT * FROM USERDATA WHERE EMAIL=%s"
        cursor.execute(sql, [email])
        result = cursor.fetchall()
        cursor.close()

        if result:
            print("not here")
            return redirect('register')

        cursor = connection.cursor()
        sql = "SELECT * FROM USERDATA WHERE USERNAME=%s"
        cursor.execute(sql, [username])
        result = cursor.fetchall()
        cursor.close()

        if result:
            return redirect('register')
        
        deafult_profile_pic = staticfiles_storage.url('resources/img/user.png')
        print(deafult_profile_pic)
        cursor = connection.cursor()
        sql = "INSERT INTO USERDATA(EMAIL, NAME, USERNAME, PASSWORD, CREATION_DATE, PROFILE_PIC) VALUES(%s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, [email, name, username, password, timestamp, deafult_profile_pic])
        cursor.close()
        return redirect('login')
        


    return render(request, 'accounts/register.html')


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        cursor = connection.cursor()
        sql = "SELECT ID, PASSWORD FROM USERDATA WHERE EMAIL=%s"
        cursor.execute(sql, [email])
        result = cursor.fetchall()
        cursor.close()

        for r in result:
            if r[1] == password:
                print(r[0])
                request.session['user_id'] = r[0]
                return redirect('index')

        return redirect('login')
    return render(request, 'accounts/login.html')


def logout(request):
    del request.session['user_id']
    return redirect('login') 


def edit_profile(request):
    user_id = request.session['user_id']
    cursor = connection.cursor()

    if request.method == 'POST':
        name = request.POST['name']
        username = request.POST['username']
        
        sql = "SELECT COUNT(*) FROM USERDATA WHERE USERNAME = %s AND ID <> %s"
        cursor.execute(sql, [username, user_id])
        count = cursor.fetchone()
        if count[0] != 0:
            return redirect('edit-profile')
        
        email = request.POST['email']
        sql = "SELECT COUNT(*) FROM USERDATA WHERE EMAIL = %s AND ID <> %s"
        cursor.execute(sql, [email, user_id])
        count = cursor.fetchone()
        if count[0] != 0:
            return redirect('edit-profile')
        
        password = request.POST['password']

        sql = "UPDATE USERDATA SET NAME=%s, USERNAME=%s, EMAIL=%s, PASSWORD=%s  WHERE ID = %s;"
        cursor.execute(sql, [name, username, email, password, user_id])
        
        if 'gender' in request.POST:
            gender = request.POST['gender']
            sql = "UPDATE USERDATA SET GENDER=%s WHERE ID = %s;"
            cursor.execute(sql, [gender, user_id])
        if 'birthday' in request.POST:
            dob = request.POST['birthday']
            sql = "UPDATE USERDATA SET DOB=%s WHERE ID = %s;"
            cursor.execute(sql, [dob, user_id])
        if 'facebook' in request.POST:
            facebook_link = request.POST['facebook']
            sql = "UPDATE USERDATA SET FACEBOOK_LINK=%s WHERE ID = %s;"
            cursor.execute(sql, [facebook_link, user_id])
        if 'twitter' in request.POST:
            twitter_link = request.POST['twitter']
            sql = "UPDATE USERDATA SET TWITTER_LINK=%s WHERE ID = %s;"
            cursor.execute(sql, [twitter_link, user_id])
        if 'phone-number' in request.POST:
            phone_number = request.POST['phone-number']
            sql = "UPDATE USERDATA SET PHONE_NUMBER=%s WHERE ID = %s;"
            cursor.execute(sql, [phone_number, user_id])

        file = request.FILES.get('profile_photo', False)
        if file: 
            fs = FileSystemStorage()
            file_new_path = fs.save(file.name, file)
            file_url = fs.url(file_new_path)
            sql = "UPDATE USERDATA SET PROFILE_PIC=%s WHERE ID = %s;"
            cursor.execute(sql, [file_url, user_id])

    sql = "SELECT NAME, USERNAME, EMAIL, PASSWORD, NVL(GENDER, ''), NVL(DOB, ''), NVL(FACEBOOK_LINK, ''), NVL(TWITTER_LINK, ''), NVL(PHONE_NUMBER, '') FROM USERDATA WHERE ID = %s;"
    cursor.execute(sql, [user_id])
    pi= cursor.fetchone()
    cursor.close()

    
    context = {
        'name': pi[0],
        'username': pi[1],
        'email': pi[2],
        'password': pi[3],
        'gender': pi[4],
        'birthday': pi[5].strftime("%Y-%m-%d"),
        'facebook_link': pi[6],
        'twitter_link': pi[7],
        'phone_number': pi[8],
        'user_id': user_id
    }

    return render(request, 'accounts/edit-profile1.html', context)
