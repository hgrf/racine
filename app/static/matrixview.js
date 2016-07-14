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

    $('#resetmatrix').click(function(event) {
        $.ajax({
           url: "/resetmatrix/" + $('#sampleid').text(),
           type: "post",
           success: function(data) {
               load_matrix_view($('#sampleid').text());
           }
        });
        event.preventDefault();
    });

    $('.changesample').click(function (event) {
        $('#childbrowser').data('target', $(this).closest('.matrixcell'));
        $('#childbrowser').modal('show');

        event.preventDefault();
    });

    // when user chooses image in childbrowser, we have to update the corresponding element
    // of the matrix and tell the server via AJAX that the matrix was modified
    $('.childimage').dblclick(function (event) {
        // update the matrix cell that this browser was opened from
        $('#childbrowser').data('target').find('a').attr('href', $(this).attr('src'));
        $('#childbrowser').data('target').find('img.sample').attr('src', $(this).attr('src'));
        $('#childbrowser').data('target').find('p').html($(this).data('name'));
        $('#childbrowser').data('target').find('.sampledescription').html($(this).data('description'));
        $('#childbrowser').modal('hide');

        id = $(this).data('id');

        // check if this sample is already attributed to some other matrix cell and remove if it's the case
        $('.matrixcell').each(function () {
            if ($(this).find('img.sample').attr('id') == id) {
                $(this).find('img.sample').attr('id', '');
                $(this).find('img.sample').attr('src', '');
                $(this).find('p').html('');
                $(this).find('.sampledescription').html('');
            }
        });

        // now update the ID of the image in the matrix cell that the browser was opened from
        $('#childbrowser').data('target').find('img.sample').attr('id', id);

        // finally, let the server know about the changed coords
        $.ajax({
            url: "/setmatrixcoords/" + id,
            type: "post",
            data: {
                "mx": $('#childbrowser').data('target').data('mx'),
                "my": $('#childbrowser').data('target').data('my')
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