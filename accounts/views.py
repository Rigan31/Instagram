from django.shortcuts import render, redirect
from django.db import connection
from django.core.files.storage import FileSystemStorage
from django.db.models.functions.datetime import datetime

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
        
        cursor = connection.cursor()
        sql = "INSERT INTO USERDATA(EMAIL, NAME, USERNAME, PASSWORD, CREATION_DATE) VALUES(%s, %s, %s, %s, %s)"
        cursor.execute(sql, [email, name, username, password, timestamp])
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
        email = request.POST['email']
        password = request.POST['password']
        gender = request.POST['gender']
        dob = request.POST['birthday']
        facebook_link = request.POST['facebook']
        twitter_link = request.POST['twitter']
        phone_number = request.POST['phone-number']

        file = request.FILES['profile_photo']
        fs = FileSystemStorage()
        file_new_path = fs.save(file.name, file)
        file_url = fs.url(file_new_path)

        sql = "UPDATE USERDATA SET NAME=%s, USERNAME=%s, EMAIL=%s, PASSWORD=%s,PHONE_NUMBER=%s, PROFILE_PIC=%s, GENDER=%s, DOB=%s, FACEBOOK_LINK=%s, TWITTER_LINK=%s  WHERE ID = %s;"
        cursor.execute(sql, [name, username, email, password, phone_number, file_url, gender, dob, facebook_link, twitter_link, user_id])

    
    sql = "SELECT NAME, USERNAME, EMAIL, PASSWORD, GENDER, DOB, FACEBOOK_LINK, TWITTER_LINK FROM USERDATA WHERE ID = %s;"
    cursor.execute(sql, [user_id])
    pi= cursor.fetchone()
    cursor.close()

    context = {
        'name': pi[0],
        'username': pi[1],
        'email': pi[2],
        'password': pi[3],
        'gender': pi[4],
        'birthday': pi[5],
        'facebook_link': pi[6],
        'twitter_link': pi[7],
        'user_id': user_id
    }

    return render(request, 'accounts/edit-profile.html', context)
