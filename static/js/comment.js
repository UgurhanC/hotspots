// Initial Search Buttons
var topics = ["Internet Cats", "Meme's", "Typing", "Space", "Rick and Morty"];
function addSearchBtns() {
  $("#buttons").html("");
  for (i = 0; i < topics.length; i++) {
    var $button = $("<input type='button' class='btn btn-sm search-btn' />");
    $button.val(topics[i]);
    $("#buttons").append($button);
  }
}
addSearchBtns();
$( document ).ready(function() {
    console.log("ready");

    $("#search-txt").on("input", function() {
        console.log("change");

    })
   $("button").on("click", function() {
       console.log("searching");
   })
  $(document).on("click","#results img",function(){
	$(this).css("border","5px solid green");
	$("#results img").not($(this)).css("border","none");
	cm_url = this.src
	//console.log(link)

});

$('.myImg').click(function(){
    imgid = this.id
});


$('#comments').click(function() {
        console.log(cm_url);
        $.ajax({
          type: "POST",
          //contentType: "application/json;charset=utf-8",
          url: "/comment",
          //traditional: "true",
          //data: JSON.stringify({cm_url}),
          data: {"cm_url": cm_url, "id": imgid},
          dataType: "text",
          });
          $("#results img").not($(this)).css("border","none");
    });
$('#giphy').hide();
$("#giphy .section").hide();


if ($('#element').is(':empty')){
  //do something
} else{
  console.log("found")
}

/*
$("#Showbutton").click(function(e){
     $('#giphy').toggle('slow');//or just show instead of toggle
}); */
$('#Showbutton').on("click", function () {
        $('#giphy').slideToggle("slow", function () {
            $(window).scrollTop($(this).offset().top + $(this).height());
        });
    });



$('#user-search').on("keyup", function () {
  var chatinput = document.getElementById("user-search").value;
    if (chatinput == "" || chatinput.length == 0 || chatinput == null)
    {
        // Invalid... Box is empty
        console.log("empty")
        $("#giphy .section").hide();




    } else {
      console.log("yay")

      $("#giphy .section").show();


    }
});



});




$(document).on("keyup", "#user-search", function giphy() {

  $('#user-search').keyup(delay(function (e) {

    $("#results").html("");
  // Beginning API call
  var queryURL = "https://api.giphy.com/v1/gifs/search?";
  var query;
  var params = {
    q: query,
    limit: 10,
    //api_key: "aFFKTuSMjd6j0wwjpFCPXZipQbcnw3vB",
    api_key: "acWYyORZmqoAwhmQACttO8SL7VGVV0Mw",
    fmt: "json"
  };
  if ($(this).hasClass("search-btn")) {
    query = $(this).val();
  } else if ($("#user-search").val() !== "") {
    query = $("#user-search").val();
    topics.push(query);
    if (topics.length > 6) {
      topics.shift();
    }
    addSearchBtns();
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
        //var $rating = $("<h6>");
        var gifObj = r.data[i];
        var gif = gifObj.images;

        // Image builder object
        $img.attr({
           //"width": "50px",
          //src: gif.fixed_height_still.url,
          src: gif.fixed_height.url,
          //"data-animate": gif.fixed_height.url,
          //"data-still": gif.fixed_height_still.url,
          //"data-state": "still",
          class: "gif"
        });
        // $div.attr("id", "gif-" + i);
        $div.addClass("gif-box");
       // $rating.text("Rating: " + gifObj.rating);
        $div.append($img);//, $rating);
        $("#results").append($div);
      }
/*
      $(".gif").on("click", function() {
        var link = this.src
        console.log(link)
        if (!this.style.border) {
        this.style.border = "3px solid blue";
        }
        else {git ad
            this.style.border = '';
        }
      });
        */









        /*
        var state = $(this).attr("data-state");
        if (state === "still") {
          $(this).attr("src", $(this).attr("data-animate"));
          $(this).attr("data-state", "animate");
        } else {
          $(this).attr("src", $(this).attr("data-still"));
          $(this).attr("data-state", "still");
        }
        */

    }
  });

  }, 500));



});

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



