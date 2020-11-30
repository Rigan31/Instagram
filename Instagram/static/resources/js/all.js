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
            var y = document.getElementsByClassName("total_likes")
    
            
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