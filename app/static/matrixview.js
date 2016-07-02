function init_matrix_view() {
    $('#submit').click(function (event) {
        $.ajax({
            url: "/matrixview/" + $('#sampleid').text(),
            type: "post",
            data: $('#newmatrixform').serialize(),
            success: function (data) {
                load_matrix_view($('#sampleid').text());
            }
        });
        event.preventDefault();
    });

    $('.matrixcell').dblclick(function (event) {
        $('#childbrowser').data('target', $(this));
        $('#childbrowser').modal('show');

        event.preventDefault();
    });

    // when user chooses image in childbrowser, we have to update the corresponding element
    // of the matrix and tell the server via AJAX that the matrix was modified
    $('.childimage').dblclick(function (event) {
        $('#childbrowser').data('target').find('a').attr('href', $(this).attr('src'));
        $('#childbrowser').data('target').find('img').attr('src', $(this).attr('src'));
        $('#childbrowser').data('target').find('p').html($(this).data('name'));

        $('#childbrowser').modal('hide');

        id = $(this).data('id');

        $('.matrixcell').each(function () {
            if ($(this).find('img').attr('id') == id) {
                $(this).find('img').attr('id', '');
                $(this).find('img').attr('src', '');
                $(this).find('p').html('');
            }
        });

        $('#childbrowser').data('target').find('img').attr('id', id);

        $.ajax({
            url: "/setmatrixcoords/" + id,
            type: "post",
            data: {
                "mx": $('#childbrowser').data('target').data('mx'),
                "my": $('#childbrowser').data('target').data('my')
            },
            success: function (data) {
            }
        });

        event.preventDefault();
    });
}

function load_matrix_view(id) {
    $.ajax({
        url: "/matrixview/" + id,
        success: function (data) {
            $("#editor-frame").html(data);
            $.ajax({
                url: "/childbrowser/" + $("#sampleid").text(),
                success: function (data) {
                    $("#childbrowser-frame").html(data);
                    init_matrix_view();
                }
            });
        }
    });
}