window.onload = function()
{
var modal = document.getElementById('myModal');
var img = $('.myImg');
var modalImg = $("#img01");
var captionText = document.getElementById("caption");

// display the images in a modal on click
$('.myImg').click(function(){
    modal.style.display = "block";
    var newSrc = this.src;
    modalImg.attr('src', newSrc);
    captionText.innerHTML = this.alt;
    // send the id of the photo to request the comments
    $.ajax({
          url: "/zien_comments",
          type: "POST",
          data: {"photo_id":this.id},
          dataType: "text",
    });

    let request = $.ajax({
      url: "/like",
      type: "GET",
      data: {"id": this.id},
    });
    request.done(update_photo_data);

});



var span = document.getElementsByClassName("close")[0];
span.onclick = function() {
  modal.style.display = "none";
}

// hide the comment section and gif lookup section when the picture is closed
$('#del').click(function(){
    $("#cmbx img").remove();
    $('#cmbx').hide()
    $('#giphy').hide()
});
$('#cmbx').hide()

// get the links from the comments posted on this picture
$('#scomments').click(function(){
    $('#cmbx').toggle();
    $('#cmbx img').remove();
    $("#giphy .section").hide();
    $.ajax({
        type: "GET",
                url: '/zien_comments',
                data: {cmlist: "cmlist"},
                success: function(cmlist){

                    for (i = 0; i < cmlist.length; i++) {
                    var elem = document.createElement("img");
                    elem.setAttribute("src", cmlist[i]);
                    document.getElementById("cmbx").appendChild(elem);
                }
            }
          });
});

// reset the gif lookup section on comment submission
$('#comments').click(function(){
    $('#cmbx').show('slow')
    $('#cmbox').html('')
    $('#giphy').hide('slow')
    $('#cmbx img').remove()
    $("#results img").remove();
    $("#results div").remove();
    $.ajax({
                type: "GET",
                url: '/zien_comments',
                data: {cmlist: "cmlist"},
                success: function(cmlist){

                    for (i = 0; i < cmlist.length; i++) {
                    var elem = document.createElement("img");
                    elem.setAttribute("src", cmlist[i]);

                    document.getElementById("cmbx").appendChild(elem);
            }
            }
          });
          document.getElementById('user-search').value = "";
});

$(document).on('click','#hart', function(event) {

});

}
