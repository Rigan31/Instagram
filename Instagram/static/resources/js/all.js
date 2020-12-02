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

function modalTheimage(x, story_path){
    var c = x.parentElement.children
    var modal = c[1]
    var modalImg = modal.children[1]
    modal.style.display = "block";
    modalImg.src = story_path;

    
}

function closeThemodal(x) { 
    x.parentElement.style.display = "none";
}

$(document).ready(function() {
  $('.edit-profile-form').on('input change', function() {
    $('.edit-profile-submit').attr('disabled', false);
  });
})