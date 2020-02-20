$(document).ready(function(){
    window.setTimeout(function () {
        $("#alert-message").fadeTo(500, 0).slideUp(500, function () {
            $(this).remove();
        });
    }, 2000);
});

