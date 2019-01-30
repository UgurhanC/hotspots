window.onload = function()
{

var modal = document.getElementById('myModal');

var img = $('.myImg');
var modalImg = $("#img01");
var captionText = document.getElementById("caption");

$('.myImg').click(function(){
    modal.style.display = "block";
    var newSrc = this.src;
    modalImg.attr('src', newSrc);
    captionText.innerHTML = this.alt;
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
$('#like').click(function(){
    console.log("likeclick")
});





$('#del').click(function(){
    $("#cmbx img").remove();
    $('#cmbx').hide()
    $('#giphy').hide()
});
$('#cmbx').hide()
$('#scomments').click(function(){
    $('#cmbx').toggle();
    //$('#cmbox').html('')
    $('#cmbx img').remove();
    $("#giphy .section").hide();

    console.log($('#cmbox').html())
    $.ajax({
        type: "GET",
                url: '/zien_comments',
                data: {cmlist: "cmlist"},
                success: function(cmlist){

                    for (i = 0; i < cmlist.length; i++) {
                    var elem = document.createElement("img");
                    elem.setAttribute("src", cmlist[i]);
                    console.log(elem.src)

                    document.getElementById("cmbx").appendChild(elem);




                }
            }
          });
});

$('#comments').click(function(){
    $('#cmbx').show('slow')
    $('#cmbox').html('')
    //$('#cmbox img').remove()
    $('#giphy').hide('slow')
    $('#cmbx img').remove()
    $("#results img").remove();
    $("#results div").remove();
    console.log($('#cmbox').html())
    $.ajax({
                type: "GET",
                url: '/zien_comments',
                data: {cmlist: "cmlist"},
                success: function(cmlist){

                    for (i = 0; i < cmlist.length; i++) {
                    var elem = document.createElement("img");
                    elem.setAttribute("src", cmlist[i]);
                    console.log(elem.src)

                    document.getElementById("cmbx").appendChild(elem);




            }
            }
          });
          document.getElementById('user-search').value = "";
          console.log($('#cmbox').html())
});

$(document).on('click','#hart', function(event) {

});

}
