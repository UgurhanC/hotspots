
function like_photo(id){
    let request = $.ajax({
      url: "/like",
      type: "POST",
      data: {"id": id},
    });
    request.done(update_photo_data);
}

function update_photo_data(data) {
    var likeCount = document.getElementById("likecount");
    likeCount.innerHTML = data.n_likes;
    console.log(data.is_liked);
    if (data.is_liked === true) {
         document.getElementById("hart").classList.remove('black');
         console.log(data.n_likes)
    } else {
         document.getElementById("hart").classList.add('black');
         console.log(data.n_likes)
    }
}


function change(){
    var elem = document.getElementById("likebutton");
    if (elem.value=="liked") elem.value = "unliked";
    else elem.value = "liked";
}



function lcm(id){
    $.ajax({
      url: "/",
      type: "POST",
      data: {"id": id},
      dataType: "text",

    });
}