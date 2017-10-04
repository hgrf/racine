function mobile_hide_sidebar() {
    $('#toggle-sidebar').removeClass('active');
    $('.sidebar').removeClass('overlay');
    $('.content-overlay').fadeOut();
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