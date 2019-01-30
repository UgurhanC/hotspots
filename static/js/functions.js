// send the photo id
function like_photo(id){
    let request = $.ajax({
      url: "/like",
      type: "POST",
      data: {"id": id},
    });
    request.done(update_photo_data);
}
// check if photo is liked by user and how many likes the photo has
function update_photo_data(data) {
    var likeCount = document.getElementById("likecount");
    likeCount.innerHTML = data.n_likes;
    if (data.is_liked === true) {
         document.getElementById("hart").classList.remove('black');
    } else {
         document.getElementById("hart").classList.add('black');
    }
}