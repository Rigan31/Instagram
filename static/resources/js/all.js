document.getElementById("like_list_inner_container").onclick = function(event){
    event.stopPropagation();
}

function close_list() {
    document.querySelector(".like_list_container").style.display = "none";
}

function like_list(user,post, x){
    var csrf = $("input[name=csrfmiddlewaretoken]").val()
    $.ajax({
        method: "GET",
        url: 'like_list',
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
        url: 'likes',
        data: {
            user_id: user,
            post_id: post,
            csrfmiddlewaretoken: csrf
        },
        success:function(response){
            $(x).toggleClass("fa-heart fa-heart-o")
            var y = x.parentElement.parentElement.parentElement
            var z = null
            for(var i = 0; i < y.children.length; i++){
                if(y.children[i].className == "text"){
                    z = y.children[i]
                    break
                }
            }

            z.children[0].innerHTML = response.count + ' likes'
            
            
        }
    })
}

function saved(user, post, x){
    var csrf = $("input[name=csrfmiddlewaretoken]").val()
    $.ajax({
        method: "POST",
        url: 'saved',
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
        url: 'follow',
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
    var modal = c[1]
    var modalImg = modal.children[1]
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
    var c = x.parentElement
    console.log(c)
    for(var i = 0; i < c.children.length; i++){
        console.log(c.children[i].className)
        if(c.children[i].className == 'dropdown-content'|| c.children[i].className == 'dropdown-content dropdown-content-show'){
            console.log(c.children[i])
            c.children[i].classList.toggle("dropdown-content-show")
            break
        }
    }
}


window.onclick = function(event) {
    if (!event.target.matches('.dropdown-icon')) {
      var dropdowns = document.getElementsByClassName("dropdown-content");
      console.log(dropdowns)
      var i;
      for (i = 0; i < dropdowns.length; i++) {
        var openDropdown = dropdowns[i];
        console.log(openDropdown)
        if (openDropdown.classList.contains('dropdown-content-show')) {
          openDropdown.classList.remove('dropdown-content-show');
        }
      }
    }
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
                "<video class=\"imageThumb\" src=\"" + e.target.result + "\" title=\"" + file.name + "\">" + "</video>"+
                "</div>");
            }
        });
        fileReader.readAsDataURL(f);
       
    }
        
}



