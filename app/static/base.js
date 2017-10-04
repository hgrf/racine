$(document).ready(function() {
    $('#toggle-sidebar').click(function () {
        if ($('.sidebar').hasClass('overlay')) {
            $('.sidebar').removeClass('overlay');
        } else {
            $('.sidebar').addClass('overlay');
        }
    });

    $('.nav-button-toggle').click(function () {
        if ($(this).hasClass('active')) {
            $(this).removeClass('active');
        } else {
            $(this).addClass('active');
        }
    });
});