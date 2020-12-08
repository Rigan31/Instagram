function inner_container_stop_propagation(){
    var e = window.event;
    e.stopPropagation();
}

function close_list() {
    document.querySelector(".like_list_container").style.display = "none";
}

function like_list(user,post, x){
    var csrf = $("input[name=csrfmiddlewaretoken]").val()
    $.ajax({
        method: "GET",
        url: 'http://' + window.location.hostname + ':' + window.location.port + '/like_list',
        data: {
            logged_user: user,
            post_id: post,
            csrfmiddlewaretoken: csrf
        },
        success:function(response){

            var code = "";
            $("#list_of_liked_users").html("")

            for(var i=0; i<response.liked_user_list.length; i++){

                var img = '<img src="' + response.liked_user_list[i].user_img + '" />';
                var img_link = '<a href="' + response.liked_user_list[i].user_link + '" class="user_list_image_link">' + img + '</a>';
                var link = '<a class="user_list_username_link" href="' + response.liked_user_list[i].user_link + '">' + response.liked_user_list[i].username + '</a>';
                var username = '<p>' + response.liked_user_list[i].user_name + '</p>';

                var text = '';
                if(response.liked_user_list[i].isFollowee) text='Unfollow';
                else if(response.liked_user_list[i].isFollower) text='Follow back';
                else text ='Follow'

                //logged_user_id = je logged in hoye ase
                //user_id = je like dise, liked user list tay ase
                //poster_id = je post dise
                var button = '<button class="follow_button_in_list" onclick="follow(this, '+response.logged_user_id+', '+response.liked_user_list[i].user_id+')">' + text + '</button>';

                if(response.logged_user_id == response.liked_user_list[i].user_id) code = '<li><div>' + img_link + link + username + '</div></li>';
                else code = '<li><div>' + img_link + link + username + button + '</div></li>'

                $("#list_of_liked_users").append(code);
            }
        }
    })
    document.querySelector(".like_list_container").style.display = "flex";
}


function likes(user, post, x){
    var csrf = $("input[name=csrfmiddlewaretoken]").val()
    $.ajax({
        method: "POST",
        url: 'http://' + window.location.hostname + ':' + window.location.port + '/likes',
        data: {
            user_id: user,
            post_id: post,
            csrfmiddlewaretoken: csrf
        },
        success:function(response){
            $(x).toggleClass("fa-heart fa-heart-o")
            var y = x.parentElement.parentElement.parentElement.parentElement
            var z = null
            for(var i = 0; i < y.children.length; i++){
                if(y.children[i].className == "text" || y.children[i].className == "text text-in-post-view"){
                    z = y.children[i]
                    break
                }
            }

            //console.log(z.children[0])
            var html = '<h4><b style="font-size: 20px" >' + response.count + '</b> likes</h4>';
            z.children[0].innerHTML = html;
            
            
        }
    })
}


function saved(user, post, x){
    var csrf = $("input[name=csrfmiddlewaretoken]").val()
    $.ajax({
        method: "POST",
        url: 'http://' + window.location.hostname + ':' + window.location.port + '/saved',
        data: {
            user_id: user,
            post_id: post,
            csrfmiddlewaretoken: csrf
        },
        success:function(response){
            $(x).toggleClass("fa-bookmark fa-bookmark-o")
    
        }
    })
}

function follow(x, user, followee){
    var csrf = $("input[name=csrfmiddlewaretoken]").val()
    console.log(user)
    console.log(followee)
    $.ajax({
        method: "POST",
        url: 'http://' + window.location.hostname + ':' + window.location.port + '/follow',
        data: {
            user_id: user,
            followee_id: followee,
            msg: x.innerHTML,
            csrfmiddlewaretoken: csrf
        },
        success:function(response){
            //$(x).toggleClass("fa-bookmark fa-bookmark-o")
            x.innerHTML = response.newMsg
    
        }
    })
}

function follow_button(x, user, followee, mm){
    var csrf = $("input[name=csrfmiddlewaretoken]").val()
    console.log(user)
    console.log(followee)
    $.ajax({
        method: "POST",
        url: 'follow-button',
        data: {
            user_id: user,
            followee_id: followee,
            msg: x.innerHTML,
            csrfmiddlewaretoken: csrf
        },
        success:function(response){
            //$(x).toggleClass("fa-bookmark fa-bookmark-o")
            x.innerHTML = response.newMsg
            if(mm == 1)
                x.parentElement.parentElement.style.display = "none"
        }
    })
}

function modalTheimage(x, story_path){
    var c = x.parentElement.children
    //var modal = c[1]
    //var modalImg = modal.children[1]

    var modal = document.getElementById('myModal');
    var modalImg = modal.children[1];

    modal.style.display = "block";
    modalImg.src = story_path;
    c[2].style.borderColor = "white"


}

function closeThemodal(x) { 
    x.parentElement.style.display = "none";
}

$(document).ready(function() {
  $('.edit-profile-form').on('input change', function() {
    $('.edit-profile-submit').attr('disabled', false);
  });

  //add active class to current element in navbar
  $(document).on('click', '.nav-icon-circle',function () {
    $('.nav-icon-circle').removeClass("nav-menu-active");
    $(this).addClass("nav-menu-active");
   });
    
})

function showDropDown(x){

    var all_dropdown = document.getElementsByClassName('dropdown-content')
    for(var i=0; i<all_dropdown.length; i++){
        var c = all_dropdown[i];

        if(c.className == 'dropdown-content dropdown-content-show') {
            c.classList.toggle("dropdown-content-show");
            break;
        }
    }
    for(var i=0; i<x.children.length; i++){
        var c = x.children[i];

        if(c.className == 'dropdown-content'|| c.className == 'dropdown-content dropdown-content-show') {
            c.classList.toggle("dropdown-content-show");
            break;
        }
    }
}

$(window).click(function(event) {
    console.log("hello world")
    if (event.target.matches('.nav-icon-circle')==false && event.target.matches('.dropdown-icon')==false) {
      var dropdowns = document.getElementsByClassName("dropdown-content");

      var i;
      for (i = 0; i < dropdowns.length; i++) {
        var openDropdown = dropdowns[i];
        console.log(openDropdown)
        if (openDropdown.classList.contains('dropdown-content-show')) {
          openDropdown.classList.remove('dropdown-content-show');
        }
      }
    }

    if(event.target.matches('.show-all-notification') == false && event.target.matches('.notification') == false){
        document.querySelector('.show-all-notification').style.display = "none";
    }
});


function search_delete(x,search, m){
    var csrf = $("input[name=csrfmiddlewaretoken]").val()
    $.ajax({
        method: "GET",
        url: 'search-delete',
        data: {
            search_id: search,
            mm: m,
            csrfmiddlewaretoken: csrf
        },
        success:function(response){
            if(m == 1){
                x.parentElement.parentElement.style.display = 'none'
            }
            else{
                var y = document.querySelectorAll('.search-history-element')
                for(var i = 0; i < y.length; i++)
                    y[i].style.display = 'none'
            }
        }
    })
}


function previewChangePhoto(input) {
    console.log("here")
    if (input.files && input.files[0]) {
      var reader = new FileReader();
      console.log("fadf")
      
      reader.onload = function(e) {
        var x = document.querySelectorAll('#edit-profile-photo-photo')
        console.log(x)
        $('#edit-profile-photo-photo').attr('src', e.target.result);
      }
      
      reader.readAsDataURL(input.files[0]); // convert to base64 string
    }
}

function showNotification(x){
    var a = window.location.protocol + "//" + window.location.host + "/notification"
    console.log(a)
    $.ajax({
        method: "GET",
        url: a,
        data: {
            
        },
        success:function(response){
            var div = document.querySelectorAll(".show-all-notification")

            for(var i = 0; i < response.notifications.length; i++){
                var photo = response.notifications[i].action_photo
                var msg = response.notifications[i].msg
                var date = response.notifications[i].date

                var img = '<img src="'+photo+'" class="">'
                var imgDiv = '<div class="show-all-notification-photo"> '+img+' </div>'

                var msgDiv = '<div class="show-all-notification-msg">'+msg+'</div>'
                var dateDiv = '<div class="show-all-notification-date">'+date+'</div'
                var msgDateDiv = '<div class="show-all-notification-msg-date">'+msgDiv+dateDiv+'</div>'
                var finalDiv = '<div class="show-all-notification-element clearfix">'+imgDiv+msgDateDiv+'</div>'
                
                $(div).append(finalDiv)
            }
            document.querySelector('.show-all-notification').style.display = "block";
        }
    })
}

/* =================================*/

function change_color_of_post_button(x){
    var p = x.parentElement;
    for(var i=0; i<p.children.length; i++){
        if(p.children[i].nodeName == "BUTTON"){
            var st1 = 'rgba(' + 0 + ',' + 149 + ',' + 246 + ',' + 0.3 + ')';
            var st2 = 'rgba(' + 0 + ',' + 149 + ',' + 246 + ',' + 1 + ')';

            if(x.value == "") {
                p.children[i].style.color = st1;
                p.children[i].disabled = true;
            }
            else {
                p.children[i].style.color = st2;
                p.children[i].disabled = false;
            }
            break;
        }
    }
}

function addComment(x, logged_user_username, logged_user_id, post_id){

    console.log('ekhane ashe');
    console.log('username ' + logged_user_username);
    console.log('user_id ' + logged_user_id);
    console.log('post_id ' + post_id);
    var xx = new Date();
    console.log('time ' + xx.getDay() + '-' + xx.getMonth() + '-' + xx.getFullYear() + ' ' + xx.getHours() + ':' + xx.getMinutes() + ':' + xx.getSeconds());

}

function load_media_container(){

    console.log('ekhane ashe');

}

var mediaIndex = 0;

function slideMedia(x, photos, videos, add){

    var div = x.parentElement;
    var img = div.children[0];
    var vid = div.children[1]
    var prev = div.children[2];
    var next = div.children[3];
    var dotDiv = div.children[4];
    var count = photos.length + videos.length;

    prev.style.display = 'block';
    next.style.display = 'block';
    for(var i=0; i<dotDiv.children.length; i++) dotDiv.children[i].style.backgroundColor = '#bbb';

    if(add==1 && mediaIndex+1<count) mediaIndex = mediaIndex+1;
    else if(add==-1 && mediaIndex-1>=0) mediaIndex = mediaIndex-1;

    if(mediaIndex == count-1) next.style.display = 'None';
    if(mediaIndex == 0) prev.style.display = 'None';

    img.style.display = 'None';
    vid.style.display = 'None';

    if(mediaIndex<photos.length){
        img.style.display = 'block';
        img.src = photos[mediaIndex];
    }else{
        vid.src = videos[mediaIndex - photos.length];
        vid.style.display = 'block';
    }
    dotDiv.children[mediaIndex].style.backgroundColor = 'deepskyblue';
}





function previewPostUpload(e){
    var files = e.target.files,
    filesLength = files.length;
    console.log('Files length: '+ filesLength);
    var div1 = document.querySelectorAll('.create-post-upload-image')
    var div2 = document.querySelectorAll('.create-post-upload-video')

    for (var i = 0; i < filesLength; i++) {
        var f = files[i]
        var fileReader = new FileReader();
        var filetype = f.type.slice(0,5)
        
        console.log(filetype)
    
        fileReader.onload = (function(e) {
                var file = e.target;
                if(filetype == 'image'){
                    console.log('here is the image')
                    $(div1).append("<div class=\"pip\">" +
                    "<img class=\"imageThumb\" src=\"" + e.target.result + "\" title=\"" + file.name + "\"/>" +
                    "</div>");
                }
                else{
                    $(div2).append("<div class=\"pip\">" +
                    "<video class=\"imageThumb\" src=\"" + e.target.result + "\" title=\"" + file.name + "\" controls >" + "</video>"+
                    "</div>");
                }
        });
        fileReader.readAsDataURL(f);
       
    }
        
}

function searchUserChat(){
    var u = window.location.protocol + "//" + window.location.host + "/search-chat-user"
    console.log(u)
    var a = document.querySelector('.search-chat-user').value
    var div = document.querySelector('.chat-search-user-list')
    var div2 = document.querySelector('.chat-user-list')
    if(a == ""){
        div.style.display = "none"
        div2.style.display = "block"
    }
    else{
        $.ajax({
            method: "GET",
            url: u,
            data:{
                value:a,
            },
            success:function(response){
                div.style.display = "block";
                div.innerHTML = ""
                div2.style.display = "none"
                for(var i = 0; i < response.chatUserList.length; i++){
                    var name = response.chatUserList[i].searchee_name
                    var id = response.chatUserList[i].searchee_id
                    var photo = response.chatUserList[i].searchee_photo

                    var img = '<img src="'+photo+'">'
                    var imgDiv = '<div class="chat-user-list-element-photo">'+img+'</div>'
                    var nameDiv = '<div class="chat-user-list-element-name" >'+name+'</div>'
                    var mainDiv = '<div class="chat-user-list-element clearfix">'+imgDiv+nameDiv+'</div>'
                    var tmp = window.location.protocol+"//"+window.location.host + "/chat-to-partner/"+id
                    var aid = '<a href="'+tmp+'">'+mainDiv+'</a>'
                    $(div).append(aid)
                }
            }
        })
    }
    
}


function sendMsg(p){
    var u = window.location.protocol + "//" + window.location.host + "/send-msg-to-partner"
    var a = document.querySelector('.send-msg-to-partner').value
    if(a != ""){
        $.ajax({
            method: "GET",
            url: u,
            data:{
                msg:a,
                partner_id: p, 
            },
            success:function(response){
                var div = document.querySelector('.chat-user-message')
                var msgDiv = '<div><text>'+a+'</text></div>'
                //var datediv = '<div>'+response.msg_date+'</div>'
                var mainDiv = '<div class="chat-msg-right clearfix">'+msgDiv+'</div>'
                var mainDiv2 = '<div class="chat-user-single-message clearfix">'+mainDiv+'</div>'
                $(div).append(mainDiv2)

                document.querySelector('.send-msg-to-partner').value = ""
            }
        })
    }

}

function updateScroll(){
    var element = document.querySelector('.chat-user-message-body');
    element.scrollTop = element.scrollHeight;
}