(function($) {
    // tell MathJax to align left even if it's not loaded yet
    window.MathJax = {
        displayAlign: "left"
    };

    // configure the CKEditor
    var ckeditorconfig = {
        filebrowserImageBrowseUrl : '/browser',
        filebrowserWindowWidth  : 800,
        filebrowserWindowHeight : 500,
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
            $('#childbrowser').data('target').find('a').attr('href', $(this).attr('src'));
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

    function init_editor() {
        $('#matrixviewbutton').click(function() {
            load_matrix_view($('#sampleid').text());
            init_matrix_view();
        });

        $('#archive').click(function() {
            $.ajax({
                url: "/togglearchived",
                type: "post",
                data: { "id": $('#sampleid').text() },
                success: function( data ) {
                    if(data.isarchived) {
                        $('#archive').attr('title', 'De-archive');
                        $('#archive').attr('src', '/static/dearchive.png');
                    } else {
                        $('#archive').attr('title', 'Archive');
                        $('#archive').attr('src', '/static/archive.png');
                    }
                }
            });
        });

        // image browser (open in new window)
        $('#browser').click(function(event) {
            window.open("/browser?sample="+$("#sampleid").text(), 'Browser', 'height=500, width=800, scrollbars=yes')
        });

        $('.editsamplename').editable('/changesamplename', {
            style: 'inherit',
            event     : "dblclick",
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
            event     : "dblclick",
            callback : function(value, settings) {
                $( "#navtype"+$('#sampleid').text() ).html(value);
            }
        });

        $('.editsampledescription').editable('/changesampledesc', {
            type: 'ckeditor',
            submit: 'OK',
            cancel: 'Cancel',
            onblur: "ignore",
            event     : "dblclick",
            ckeditor: ckeditorconfig
        });

        $('.editactiondate').editable('/changeactiondate', {
            style: 'inherit',
            submit: 'OK',
            event     : "dblclick",
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
            submit : 'OK',
            event     : "dblclick"
        });

        function beforeunload_handler(e) {
            confirmationMessage = "Are you sure you want to leave before saving modifications?";
            e.returnValue = confirmationMessage;     // Gecko, Trident, Chrome 34+
            return confirmationMessage;              // Gecko, WebKit, Chrome <34
        }

        // TODO: better way to solve problem with images and latex would be to just re-load the action from the server
        // before editing
        $(".editactiondescription").editable('/changeactiondesc', {
            type   : 'ckeditor',
            submit : '<button type="submit" class="ok">OK</button><button type="submit" class="precancel">Cancel</button>',
            //cancel : 'Cancel',
            cancel:  '<button type="submit" class="cancel" style="display:None;"></button>',
            onblur: "ignore",
            event     : "edit",
            ckeditor : ckeditorconfig,
            data: function(value) {
                window.addEventListener('beforeunload', beforeunload_handler);

                // need to remove lightbox link from images
                $val = $('<div>'+value+'</div>');
                $val.find('img').unwrap();
                return $val.html();
            },
            callback: function() {
                // typeset all equations in this action
                MathJax.Hub.Queue(["Typeset",MathJax.Hub,$(this).get()]);

                // put back lightbox link around images
                $(this).find('img').wrap(function() { return '<a class="lightboxlink" href="'+this.src+'" data-lightbox="'+$('#sampleid').text()+'">'; });

                window.removeEventListener('beforeunload', beforeunload_handler);
            },
            onreset: function() {
                window.removeEventListener('beforeunload', beforeunload_handler);
            }
        });

        $(".editactiondescription").dblclick( function(event) {
            // see https://github.com/mathjax/mathjax-docs/wiki/Obtaining-the-original-TeX-from-a-rendered-page
            var HTML = MathJax.HTML, jax = MathJax.Hub.getAllJax($(this).get());
            for (var i = 0, m = jax.length; i < m; i++) {
                var script = jax[i].SourceElement(), tex = jax[i].originalText;
                if (script.type.match(/display/)) {
                    tex = "\\[" + tex + "\\]"
                } else {
                    tex = "\\(" + tex + "\\)"
                }
                jax[i].Remove();
                var preview = script.previousSibling;
                if (preview && preview.className === "MathJax_Preview") {
                    preview.parentNode.removeChild(preview);
                }
                preview = HTML.Element("span", {className: "MathJax_Preview"}, [tex]);
                script.parentNode.insertBefore(preview, script);
            }

            // trigger the jEditable
            $(this).trigger("edit");

            // prepare the handler for the cancel event (the "precancel" is needed so that we can execute mathjax stuff
            // after the jEditable has put the original div back)
            $(".precancel").click(function (event) {
                event.preventDefault();

                // yet another trick to get the ID of the modified action
                actionid = $(this).parent().parent().attr('id');

                // execute the "cancel" handler of the jEditable
                $(this).parent().find('.cancel').trigger('click');

                // typeset only this action
                MathJax.Hub.Queue(["Typeset",MathJax.Hub, $("div#"+actionid+".editactiondescription").get()]);
            });
        })

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

        $('.swapaction').click( function(event) {
            sampleid = $('#sampleid').text();
            actionid = $(this).data('id');
            swapid = $(this).data('swapid');
            $.ajax({
                url: "/swapactionorder",
                type: "post",
                data: { "actionid": actionid,
                        "swapid": swapid },
                success: function( data ) {
                    load_sample(sampleid);
                }
            });
        });

        // put lightbox link around images
        $('.actiondescription').find('img').wrap(function() { return '<a class="lightboxlink" href="'+this.src+'" data-lightbox="'+$('#sampleid').text()+'">'; });
        $('#sampleimage').wrap(function() { return '<a class="lightboxlink" href="'+this.src+'" data-lightbox="'+$('#sampleid').text()+'">'; });

        // typeset all equations
        MathJax.Hub.Queue(["Typeset",MathJax.Hub]);
    }

    function beforeunload_handler2(e) {
        if(CKEDITOR.instances.description.checkDirty()) {
            confirmationMessage = "Are you sure you want to leave before saving modifications?";
            e.returnValue = confirmationMessage;     // Gecko, Trident, Chrome 34+
            return confirmationMessage;              // Gecko, WebKit, Chrome <34
        }
    }

    function load_sample(id) {
        hideparentactions = ($('#parentactions').text().split(' ')[0] == 'Show');           // that's a kind of ugly workaround to read out the current status
        
        if($('#sampleid').text() != "")
            $('#'+$('#sampleid').text()+".nav-entry").css("background-color", "transparent");

        $.ajax({
            url: "/sample/"+id+(hideparentactions ? "?hideparentactions=1" : ""),
            data: { "editorframe": true },
            success: function( data, id ) {
                $( "#editor-frame" ).html(data);
                window.history.pushState({"html": data, "pageTitle": data.pageTitle}, "", "/sample/"+ $('#sampleid').text());
                init_editor();

                $('#'+$('#sampleid').text()+".nav-entry").css("background-color", "#BBBBFF");

                ckeditorconfig.filebrowserImageBrowseUrl = '/browser?sample='+$("#sampleid").text();
                CKEDITOR.replace( 'description', ckeditorconfig);
                window.addEventListener('beforeunload', beforeunload_handler2);
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

    $.event.props.push('dataTransfer');   // otherwise jQuery event does not have function dataTransfer

    $(document).ready(function() {

        // initialise sample navigation bar
        $('.nav-entry').dblclick( function( event ) {
            // this is a bit redundant with the TWO other page unload handlers, maybe want to tidy that shit up
            if($('#sampleid').text() != "" && CKEDITOR.instances.description.checkDirty()) {        // CKEDITOR.instances.description does not exist if no sample is open
                if (confirm('Are you sure you want to navigate away from this page? Press OK to continue, or Cancel to stay on the current page.')) {
                    load_sample($(this).attr('id'));
                }
            } else {
                load_sample($(this).attr('id'));
            }
            event.preventDefault();
        });

        // this function adds a glyphicon to the nav-entry $target
        function addGlyphicon($target) {
            if($($target.data('target')).is(":hidden"))
                $target.prepend('<span class="glyphicon glyphicon-expand"></span>');
            else
                $target.prepend('<span class="glyphicon glyphicon-collapse-down"></span>');

            // change the glyphicons when items are expanded or collapsed
            $($target.data('target')).on("show.bs.collapse", function(e){
               // the event goes up like a bubble and so it can affect parent nav-entries, if we do not pay
               // attention where the event comes from
               if($(this).attr('id') != e.target.id)
                   return;
               // $(this) now corresponds to the children container, we need to access the corresponding
               // nav-entry using $(this).prev()
               $(this).prev().children('.glyphicon').remove();
               $(this).prev().prepend('<span class="glyphicon glyphicon-collapse-down"></span>');
            });
            $($target.data('target')).on("hide.bs.collapse", function(e){
               if($(this).attr('id') != e.target.id)
                   return;
               $(this).prev().children('.glyphicon').remove();
               $(this).prev().prepend('<span class="glyphicon glyphicon-expand"></span>');
            });
        }

        function removeGlyphicon($target) {
            $target.children('.glyphicon').remove();
            $($target.data('target')).off('show.bs.collapse');
            $($target.data('target')).off('hide.bs.collapse');
        }

        // add glyphicons to expandable items in the navbar
        $('.nav-entry').each(function() {
           if($($(this).data('target')).children().length > 0) {
               addGlyphicon($(this));
           }
        });

        // initialise editor if sample is loaded
        if($("#sampleid").text() != "")
        {
            init_editor();
            ckeditorconfig.filebrowserImageBrowseUrl = '/browser?sample='+$("#sampleid").text();
            CKEDITOR.replace( 'description', ckeditorconfig);
            window.addEventListener('beforeunload', beforeunload_handler2);
        }


        // sample drag and drop in navigation bar
        $('.nav-entry').on({
            dragstart: function(event) {
                event.dataTransfer.setData('sampleid', event.target.id);
                event.dataTransfer.setData('text/html', '<a href="/sample/'+event.target.id+'">'+$(event.target).data('name')+'</a> ');
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
                var draggedId = event.dataTransfer.getData('sampleid');
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
                                if($("#children"+parentId).children().length == 0) {
                                    // no children yet, so need to put glyphicon
                                    addGlyphicon($("#children"+parentId).prev());
                                }
                                if(draggedItem.parent().children().length == 1)
                                {
                                    // there will be no children left after drag/drop, so remove glyphicon
                                    removeGlyphicon(draggedItem.parent().prev());
                                }
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
                    if(type=="share") {
                        if(data.code==2) // if the user removed himself from the sharer list
                            location.href = "/";
                        $('#sharelistentry'+data.shareid).remove();
                    }
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
                                $('#sharelist').append('<div class="row sharelistentry" id="sharelistentry'+data.shareid+'">'+data.username+'<img style="cursor: pointer; float: left; display: inline;" width="32" height="32" src="/static/delete.png" data-type="share" data-id="'+data.shareid+'" data-toggle="modal" data-target="#confirm-delete"></div>');
                                $('#userbrowser').modal('hide');
                            }
                        }); // what if we drag parent to child?
                    });
                }
            });
        });
    });
})(jQuery);