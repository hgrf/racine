(function($) {
    var ckeditorconfig = {
        toolbar:
        [
            ['Bold', 'Italic', 'Underline','Subscript','Superscript', 'Format', 'Styles', '-', 'NumberedList', 'BulletedList', 'HorizontalRule', '-', 'Link', 'Unlink', '-', 'Image', 'Table', 'SpecialChar', '-', 'Maximize'],
            ['UIColor']
        ]
    };

    function init_matrix_view() {
        $('#submit').click( function(event) {
            $.ajax({
                url: "/matrixview/"+$('#sampleid').text(),
                type: "post",
                data: $('#newmatrixform').serialize(),
                success: function( data ) {
                    load_matrix_view($('#sampleid').text());
                }
            });
            event.preventDefault();
        });

        $('.matrixcell').dblclick( function( event ) {
            $('#childbrowser').data('target', $(this));
            $('#childbrowser').modal('show');

            event.preventDefault();
        });

        // when user chooses image in childbrowser, we have to update the corresponding element
        // of the matrix and tell the server via AJAX that the matrix was modified
        $('.childimage').dblclick( function( event ) {
            $('#childbrowser').data('target').find('img').attr('src', $(this).attr('src'));
            $('#childbrowser').data('target').find('p').html($(this).data('name'));

            $('#childbrowser').modal('hide');

            id = $(this).data('id');

            $('.matrixcell').each(function () {
                if($(this).find('img').attr('id') == id) {
                    $(this).find('img').attr('id', '');
                    $(this).find('img').attr('src', '');
                    $(this).find('p').html('');
                }
            });

            $('#childbrowser').data('target').find('img').attr('id', id);

            $.ajax({
                url: "/setmatrixcoords/"+id,
                type: "post",
                data: { "mx": $('#childbrowser').data('target').data('mx'), "my": $('#childbrowser').data('target').data('my')},
                success: function( data ) {
                }
            });

            event.preventDefault();
        });
    }

    function init_editables() {
        $('.editsamplename').editable('/changesamplename', {
            style: 'inherit',
            callback : function(value, settings) {
                var json = $.parseJSON(value);
                $( ".editsamplename" ).html(json.name);
                if(json.code == 0) {
                    $("#navname" + json.id).html(json.name);
                } else {
                    $( "#flashmessages" ).append(begin_flashmsg+json.error+end_flashmsg);
                }
            }
        });

        $('.selectsampletype').editable('/changesampletype', {
            data   : sampletypes,
            style  : 'inherit',
            type   : 'select',
            submit : 'OK',
            callback : function(value, settings) {
                $( "#navtype"+$('#sampleid').text() ).html(value);
            }
        });

        $('.editsampledescription').editable('/changesampledesc', {
            type: 'ckeditor',
            submit: 'OK',
            cancel: 'Cancel',
            onblur: "ignore",
            ckeditor: ckeditorconfig
        });

        $('.editactiondate').editable('/changeactiondate', {
            style: 'inherit',
            submit: 'OK',
            callback : function(value, settings) {
                var json = $.parseJSON(value);
                $( "#"+json.id+".editactiondate" ).html(json.date);
                if(json.code != 0) {
                    $( "#flashmessages" ).append(begin_flashmsg+json.error+end_flashmsg);
                }
            }
        });

        $('.selectactiontype').editable('/changeactiontype', {
            data   : actiontypes,
            style  : 'inherit',
            type   : 'select',
            submit : 'OK'
        });

        $(".editactiondescription").editable('/changeactiondesc', {
            type   : 'ckeditor',
            submit : 'OK',
            cancel : 'Cancel',
            onblur: "ignore",
            ckeditor : ckeditorconfig
        });

        $('#submit').click( function(event) {
            for ( instance in CKEDITOR.instances ) CKEDITOR.instances[instance].updateElement(); // otherwise content of editor is not transmitted
            $.ajax({
                url: "/newaction/"+$('#sampleid').text(),
                type: "post",
                data: $('#newactionform').serialize(),
                success: function( data ) {
                    load_sample($('#sampleid').text());
                }
            });
            event.preventDefault();
        });
    }

    function load_sample(id) {
        if($('#sampleid').text() != "")
            $('#'+$('#sampleid').text()+".nav-entry").css("background-color", "transparent");

        $.ajax({
            url: "/sample/"+id,
            data: { "editorframe": true },
            success: function( data, id ) {
                $( "#editor-frame" ).html(data);
                window.history.pushState({"html": data, "pageTitle": data.pageTitle}, "", "/sample/"+ $('#sampleid').text());
                init_editables();
                init_sharelist();


                $('#matrixviewbutton').click(function() {
                    load_matrix_view($('#sampleid').text());
                    init_matrix_view();
                });

                $('#'+$('#sampleid').text()+".nav-entry").css("background-color", "#BBBBFF");

                CKEDITOR.replace( 'description', ckeditorconfig);
                // CAUTION! this solution might fill the RAM in the long term
                // (because we recreate callback functions and stuff everytime we open a different sample)
            }
        });
    }

    function load_matrix_view(id) {
        $.ajax({
            url: "/matrixview/"+id,
            success: function( data ) {
                $("#editor-frame").html(data);
                $.ajax({
                    url: "/childbrowser/"+$("#sampleid").text(),
                    success: function(data) {
                        $("#childbrowser-frame").html(data);
                        init_matrix_view();
                    }
                });
            }
        });
    }

    function init_sharelist() {
        $(".removeshare").click(function(event) {
            $.ajax({
                url: "/removeshare",
                type: "post",
                data: { "id": $('#sampleid').text(), "sharer": $(this).attr('id') },
                success: function( data ) {
                    if(data.code == 2) {        // if the user removed himself from the sharer list
                        location.href = "/";
                    }
                    $('#sharelistentry'+data.userid).remove();
                }
            }); // what if we drag parent to child?
        });
    }

    $.event.props.push('dataTransfer');   // otherwise jQuery event does not have function dataTransfer

    $(document).ready(function() {

        // initialise sample navigation bar
        $('.nav-entry').dblclick( function( event ) {
            load_sample($(this).attr('id'));
            event.preventDefault();
        });

        // initialise editor if sample is loaded
        if($("#sampleid").text() != "")
        {
            init_editables();
            init_sharelist();
            CKEDITOR.replace( 'description', ckeditorconfig);
        }


        // sample drag and drop in navigation bar
        $('.nav-entry').on({
            dragstart: function(event) {
                event.dataTransfer.setData('text', event.target.id);
            },
            dragenter: function(event) {
                event.preventDefault();
            },
            dragover: function(event) {
                $(this).css("background-color", "#BBBBFF");
                event.preventDefault();
            },
            dragleave: function(event) {
                $(this).css("background-color", "transparent");
            },
            drop: function(event) {
                var draggedId = event.dataTransfer.getData('text');
                var parentId = $(this).attr('id');
                if(draggedId == parentId) return;
                event.preventDefault();
                $.ajax({
                    url: "/changeparent",
                    type: "post",
                    data: { "id": draggedId, "parent": parentId },
                    success: function( data ) {
                        if(data == "") {
                            var draggedItem = $( "#"+draggedId+".nav-container" );
                            if(parentId != 0) {
                                draggedItem.appendTo("#children"+parentId);
                            } else {
                                draggedItem.appendTo("#root");
                            }
                        } else {
                            $( "#flashmessages" ).append("{{ begin_flashmsg|safe }}"+data+"{{ end_flashmsg|safe }}");
                        }
                    }
                }); // what if we drag parent to child?
                $(this).css("background-color", "transparent");
            }
        });

        // sample and action deletion
        $('#confirm-delete').on('show.bs.modal', function(e) {
            $(this).find('.btn-ok').attr('id', $(e.relatedTarget).data('id'));
            $(this).find('.btn-ok').data('type', $(e.relatedTarget).data('type'));
            $('.debug-id').html('Delete <strong>'+$(e.relatedTarget).data('type')+'</strong> ID: <strong>' + $(this).find('.btn-ok').attr('id') + '</strong>');
        });

        $('.btn-ok').click( function(event) {
            var type = $(this).data('type');
            var id = $(this).attr('id');
            $.ajax({
                url: "/del"+type+"/"+id,
                success: function( data ) {
                    if(type=="sample")
                        location.href = "/";
                    if(type=="action")
                        $('#'+id+'.list-entry').remove();
                    $('#confirm-delete').modal('hide');
                }
            });
        });

        // user browser
        $('#userbrowser').on('show.bs.modal', function(e) {
            $.ajax({
                url: "/userlist",
                type: "post",
                data: { "id": $('#sampleid').text() },
                success: function( data ){
                    $("#userbrowser-frame").html(data);

                    $('.user').dblclick( function( event ) {
                        $.ajax({
                            url: "/sharesample",
                            type: "post",
                            data: { "id": $('#sampleid').text(), "sharewith": $(this).attr('id') },
                            success: function( data ) {
                                $('#sharelist').append('<div class="row" id="sharelistentry'+data.userid+'"><div class="col-md-10">'+data.username+'</div><div class="col-md-2"><button class="removeshare btn btn-danger" id="'+data.userid+'">X</button></div></div>');
                                $('#userbrowser').modal('hide');

                                init_sharelist();
                            }
                        }); // what if we drag parent to child?
                    });
                }
            });
        });

        // image browser
        $('#browser').on('show.bs.modal', function(e) {
            function load_address(address) {
                $.ajax({
                    url: "/browser"+address,
                    success: function( data ) {
                        $( "#browser-frame" ).html(data);
                        init_browser();
                        // CAUTION! this solution might fill the RAM in the long term
                        // (because we recreate callback functions and stuff everytime we open a different folder)
                    }
                });
            }

            function init_browser() {
                $('.folder').dblclick( function( event ) {
                    load_address("/"+$(this).data('url'));
                    event.preventDefault();
                });

                $('.file').dblclick( function( event ) {
                    $('#sampleimage').attr("src", $(this).attr("src"));

                    $.ajax({
                        url: "/changesampleimage",
                        type: "post",
                        data: { "id": $('#sampleid').text(), "value": $(this).attr("src") }
                    });

                    $('#browser').modal('hide');
                });
            }

            load_address("");
            init_browser();         // TODO: is this line necessary? (see load_address)
        });
    });
})(jQuery);