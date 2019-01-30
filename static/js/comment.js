$( document ).ready(function() {
  // select an image by putting a border around it and remembering the id when clicked
  $(document).on("click","#results img",function(){
    	$(this).css("border","5px solid green");
    	$("#results img").not($(this)).css("border","none");
    	cm_url = this.src
});

$('.myImg').click(function(){
    imgid = this.id
});

// send the id of the image and the url of the gif for submission
$('#comments').click(function() {
        $.ajax({
          type: "POST",
          url: "/comment",
          data: {"cm_url": cm_url, "id": imgid},
          dataType: "text",
          });
          $("#results img").not($(this)).css("border","none");
    });
$('#giphy').hide();
$("#giphy .section").hide();

// show the gif lookup section
$('#Showbutton').on("click", function () {
        $('#giphy').slideToggle("slow", function () {
            $(window).scrollTop($(this).offset().top + $(this).height());
        });
    });

// show the requested gifs when the user types and hide them when the user stops typing
$('#user-search').on("keyup", function () {
  var chatinput = document.getElementById("user-search").value;
    if (chatinput == "" || chatinput.length == 0 || chatinput == null)
    {
        $("#giphy .section").hide();
    } else {
      $("#giphy .section").show();
    }
});



});



// when user stops typing request the gifs
$(document).on("keyup", "#user-search", function giphy() {

  $('#user-search').keyup(delay(function (e) {

    $("#results").html("");
  // Beginning API call
  var queryURL = "https://api.giphy.com/v1/gifs/search?";
  var query;
  var params = {
    q: query,
    limit: 10,
    api_key: "acWYyORZmqoAwhmQACttO8SL7VGVV0Mw",
    fmt: "json"
  };
  if ($(this).hasClass("search-btn")) {
    query = $(this).val();
  } else if ($("#user-search").val() !== "") {
    query = $("#user-search").val();
  }
  params.q = query;

  if ($(this).hasClass("trending")) {
    queryURL = "https://api.giphy.com/v1/gifs/trending?";
    delete params.q;
  }
  $.ajax({
    url: queryURL + $.param(params),
    method: "GET",
    success: function(r) {
      for (i = 0; i < params.limit; i++) {
        var $img = $("<img>");
        var $div = $("<div>");
        var gifObj = r.data[i];
        var gif = gifObj.images;

        // Image builder object
        $img.attr({
          src: gif.fixed_height.url,
          class: "gif"
        });
        $div.addClass("gif-box");
        $div.append($img);//, $rating);
        $("#results").append($div);
      }

    }
  });

  }, 500));



});
// timer between user-input and api request
function delay(callback, ms) {
  var timer = 0;
  return function() {
    var context = this, args = arguments;
    clearTimeout(timer);
    timer = setTimeout(function () {
      callback.apply(context, args);
    }, ms || 0);
  };
}



