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

function follow_button(x, user, followee){
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



