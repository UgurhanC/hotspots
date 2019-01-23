
function like_photo(id){
    $.ajax({
      url: "/like",
      type: "POST",
      data: {"id": id},
      dataType: "text",

    });
}