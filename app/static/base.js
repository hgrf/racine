function mobile_hide_sidebar() {
    $('#toggle-sidebar').removeClass('active');
    $('.sidebar').removeClass('overlay');
    $('.content-overlay').fadeOut();
}

function error_dialog(message) {
    // TODO: think about uniting this with flash messages
    $("#errordialog").find(".modal-body").text(message);
    $("#errordialog").modal("show");
}

$(document).ready(function() {
    $('#toggle-sidebar').click(function () {
        if ($('.sidebar').hasClass('overlay')) {
            $('.sidebar').removeClass('overlay');
            $('.content-overlay').fadeOut();
        } else {
            $('.sidebar').addClass('overlay');
            $('.content-overlay').fadeIn();
        }
    });

    $('.content-overlay').click(function() {
        mobile_hide_sidebar();
    });

    $('.nav-button-toggle').click(function () {
        if ($(this).hasClass('active')) {
            $(this).removeClass('active');
        } else {
            $(this).addClass('active');
        }
    });
});