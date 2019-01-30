$(".toggle-password").click(function() {

// https://itsolutionstuff.com/post/bootstrap-show-hidetoggle-password-input-field-using-bootstrap-show-passwordjs-pluginexample.html

// (un)show password
  $(this).toggleClass("fa-eye fa-eye-slash");
  var input = $($(this).attr("toggle"));
  if (input.attr("type") == "password") {
    input.attr("type", "text");
  } else {
    input.attr("type", "password");
  }
});