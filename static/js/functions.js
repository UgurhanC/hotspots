
function like_photo(id){
    $.ajax({
      url: "/like",
      type: "POST",
      data: {"id": id},
      dataType: "text",

    });
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