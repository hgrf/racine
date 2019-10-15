var sample_id;
var showparentactions = false;

// configure the CKEditor
var ckeditorconfig = {
    extraPlugins: 'save',
    imageUploadUrl: '/browser/upload?caller=ckdd&type=img',
    uploadUrl: '/browser/upload?caller=ckdd&type=att',
    filebrowserImageBrowseUrl: '/browser',
    filebrowserImageUploadUrl: '/browser/upload?caller=ckb&type=img',
    filebrowserLinkUploadUrl: '/browser/upload?caller=ckb&type=att',
    filebrowserWindowWidth: 800,
    filebrowserWindowHeight: 500,
	toolbarGroups: [
		{ name: 'clipboard', groups: [ 'clipboard', 'undo' ] },
		{ name: 'editing', groups: [ 'find', 'selection', 'spellchecker', 'editing' ] },
		{ name: 'forms', groups: [ 'forms' ] },
		{ name: 'document', groups: [ 'mode', 'document', 'doctools' ] },
		{ name: 'others', groups: [ 'others' ] },
		{ name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ] },
		{ name: 'styles', groups: [ 'styles' ] },
		{ name: 'paragraph', groups: [ 'list', 'indent', 'blocks', 'align', 'bidi', 'paragraph' ] },
		{ name: 'links', groups: [ 'links' ] },
		{ name: 'insert', groups: [ 'insert' ] },
		{ name: 'colors', groups: [ 'colors' ] },
		{ name: 'about', groups: [ 'about' ] },
		{ name: 'tools', groups: [ 'tools' ] }
	],
    removeButtons: 'Cut,Copy,Paste,PasteText,PasteFromWord,Undo,Redo,BGColor,RemoveFormat,Outdent,Indent,Blockquote,About,Strike,Scayt,Anchor,Source'
};

$.event.props.push('dataTransfer');   // otherwise jQuery event does not have function dataTransfer

function show_in_navbar(id, flash) {
    // make sure all parent samples are expanded in navbar
    $('#nav-entry'+id).parents('.nav-children').collapse('show');

    // scroll to the sample
    scrollval = $('#nav-entry'+id).offset().top-$('#navbar').height();
    if(scrollval != 0) {
        $('div#sidebar')
            .stop()
            .animate({scrollTop: scrollval + $('div#sidebar').scrollTop()}, 1000);
    }

    if(flash) {
        old_background = $('#nav-entry' + id).css("background-color");
        // flash the sample
        $('#nav-entry' + id)
            .stop()
            .delay(scrollval ? 1000 : 0)
            .queue(function (next) {
                $(this).css("background-color", "#FFFF9C");
                next();
            })
            .delay(1000)
            .queue(function (next) {
                $(this).css("background-color", old_background);
                next();
            });
    }
}

function init_editor(scrolltotop) {
    // define default values for arguments
    var scrolltotop = typeof scrolltotop !== 'undefined' ? scrolltotop : true;
  
    sample_id = $('#sampleid').text();

    // scroll to top
    if(scrolltotop)
        $('html, body').scrollTop(0);

    // handler for matrix view button
    $('#matrixviewbutton').click(function() {
        load_matrix_view(sample_id);
    });

    // handler for archive button
    $('#archive').click(function() {
        $.ajax({
            url: "/togglearchived",
            type: "post",
            data: { "id": sample_id },
            success: function( data ) {
                if(data.isarchived) {
                    $('#archive').attr('title', 'De-archive');
                    $('#archive').attr('src', '/static/images/dearchive.png');
                    $('#nav-entry'+sample_id).addClass('nav-entry-archived');
                } else {
                    $('#archive').attr('title', 'Archive');
                    $('#archive').attr('src', '/static/images/archive.png');
                    $('#nav-entry'+sample_id).removeClass('nav-entry-archived');
                }
            }
        });
    });

    $('#showinnavigator').click(function() {
        show_in_navbar(sample_id, true);
    });

    $('#scrolltobottom').click(function() {
       $('html, body').stop().animate({scrollTop: $('div#editor-frame').height()}, 1000);
    });

    $('#showparentactions').click(function() {
        showparentactions = !showparentactions; // toggle
        load_sample($('#sampleid').text());
    });

    // handler for button that changes sample image
    $('#changesampleimage').click(function(event) {
        window.open("/browser?changesampleimage=1&sample="+sample_id, 'Browser', 'height=500, width=800, scrollbars=yes');
        event.preventDefault();
    });

    // handler for new action submit button
    $('#submit').click( function(event) {
        // prevent "normal" submission of form
        event.preventDefault();

        // check if the user is still modifying any actions before submitting the new one
        close_editors = false;
        for(var i in CKEDITOR.instances) {
            if(i != "description" && CKEDITOR.instances[i].checkDirty()) {
                if (close_editors || confirm("You have been editing the sample description or one or more past " +
                    "actions. Your changes will be lost if you do not save them, are you sure you want to continue?")) {
                    close_editors = true;
                    CKEDITOR.instances[i].destroy();
                } else return;
            }
        }

        // make sure content of editor is transmitted
        // NB: it might be sufficient to do this only for CKEDITOR.instances["description"]
        // NB: this messes with the checkDirty() test, so have to do it after the above verification
        for(instance in CKEDITOR.instances) CKEDITOR.instances[instance].updateElement();

        $.ajax({
            url: "/newaction/"+sample_id,
            type: "post",
            data: $('#newactionform').serialize(),
            success: function( data ) {
                if(data.code != 0) {
                    // form failed validation; because of invalid data or expired CSRF token
                    // we still reload the sample in order to get a new CSRF token, but we
                    // want to keep the text that the user has written in the description field
                    $(document).one("editor_initialised", data, function(event) {
                        CKEDITOR.instances.description.setData(event.data.description);
                        error_dialog("Form is not valid. Either you entered an invalid date or the session has " +
                            "expired. Try submitting again.");
                    });
                }
                load_sample(sample_id, false, false);
            },
            error: function( jqXHR, textStatus ) {
                error_dialog("Could not connect to the server. Please make sure you are connected and try again.");
            }
        });
    });

    // catch internal links
    $('a').click(function(event) {
        if(typeof $(this).attr('href') == 'string' && $(this).attr('href').startsWith('/sample/')) {
            event.preventDefault();
            load_sample($(this).attr('href').split('/')[2]);
        }
    });

    // put lightbox link around images
    $('#sampledescription').find('img').wrap(function() { return '<a class="lightboxlink" href="'+this.src+'" data-lightbox="'+sample_id+'">'; });
    $('.actiondescription').find('img').wrap(function() { return '<a class="lightboxlink" href="'+this.src+'" data-lightbox="'+sample_id+'">'; });
    $('#sampleimage').wrap(function() { return '<a class="lightboxlink" href="'+this.src+'" data-lightbox="'+$('#sampleid').text()+'">'; });

    // typeset all equations
    if(typeof(MathJax) !== 'undefined' && MathJax.isReady)         // if it is not ready now, it should typeset automatically once it is ready
        MathJax.Hub.Queue(["Typeset",MathJax.Hub]);

    // tell CKEditor browser to pass on sample ID
    ckeditorconfig.filebrowserImageBrowseUrl = '/browser?sample='+sample_id;
    CKEDITOR.replace('description', ckeditorconfig);

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // set up editables (i.e. in-situ editors)

    // add a trigger image to all editables
    $('.editable').setup_triggers();

    // set up editors for sample and action descriptions (CKEditors)
    $('.ckeditable').ckeditable();

    // other editables:
    $('#samplename.editable').texteditable();
    $('#samplename.editable').on('editableupdate', function(event, data) {
        if(!data.code) // only if no error occured
            $("#nav-entry"+sample_id+" > .nav-entry-name").html(data.value);
    });
    $('.actiondate.editable').texteditable();

    $('.swapaction').click( function(event) {
        sampleid = sample_id;
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

    $(document).trigger("editor_initialised");
}

function load_sample(id, pushstate, scrolltotop) {
    // define default values for arguments
    var pushstate = typeof pushstate !== 'undefined' ?  pushstate : true;
    var scrolltotop = typeof scrolltotop !== 'undefined' ? scrolltotop : true;

    // if currently viewing a sample (not welcome page) then change the navbar background to transparent before loading
    // the new sample
    if($('#sampleid').text() != "")
        $('#nav-entry' + sample_id).css("background-color", "transparent");

    // load the sample data and re-initialise the editor
    $.ajax({
        url: "/editor/"+id+(showparentactions ? "?showparentactions=1" : ""),
        pushstate: pushstate,
        scrolltotop: scrolltotop,
        success: function( data ) {
            $( "#editor-frame" ).html(data);
            sample_id = $('#sampleid').text();
            if(this.pushstate)
                window.history.pushState({"id": sample_id, "pageTitle": data.pageTitle}, "", "/sample/"+ sample_id);
            document.title = "MSM - "+$('#samplename').text();
            init_editor(this.scrolltotop);
            // highlight in navbar, if the navbar is already loaded
            if($('#nav-entry'+sample_id).length) {
                $('#nav-entry'+sample_id).css("background-color", "#BBBBFF");
                show_in_navbar(sample_id, false);
            }
        },
        error: function() {
            error_dialog('Sample #'+sample_id+" does not exist or you do not have access to it.");
        }
    });
}

function before_unload_handler(e) {
    for(var i in CKEDITOR.instances) {
        if(CKEDITOR.instances[i].checkDirty()) {
            confirmationMessage = "Are you sure you want to leave before saving modifications?";
            e.returnValue = confirmationMessage;     // Gecko, Trident, Chrome 34+
            return confirmationMessage;              // Gecko, WebKit, Chrome <34
        }
    }
}

$(document).ready(function() {
    window.addEventListener("popstate", function(e) {
        if(e.state != null)
            load_sample(e.state.id, false);
        else
            location.href = "/";
    });

    // load sample if we're not on welcome page
    if(typeof sample == "undefined") {
        $.ajax({
            url: "/welcome",
            success: function(data) {
                $("#editor-frame").html(data);
            }
        });
    } else {
        load_sample(sample, false);
    }

    // add window unload handler (which asks the user to confirm leaving the page when one of the CKEditor instances
    // has been modified
    window.addEventListener('beforeunload', before_unload_handler);

    // TODO: this stuff belongs in "main.js"

    function shareselected(event, suggestion) {
        $.ajax({
            url: "/createshare",
            type: "post",
            data: { "sampleid": sample_id, "username": $('#username').val() },
            success: function( data ) {
                $('#userbrowser').modal('hide');
                $('#sharelist').append('<div class="sharelistentry" id="sharelistentry' + data.shareid + '"><a data-type="share" data-id="' + data.shareid + '" data-toggle="modal" data-target="#confirm-delete" href=""><i class="glyphicon glyphicon-remove"></i></a>\n' + data.username + '</div>');
            },
            error: function( request, status, message ) {
                $('#userbrowser').modal('hide');
                error_dialog(request.responseJSON.error);
            }
        });
    }

    // set up the OK button and the enter button
    $('#userbrowserok').click(shareselected);
    $('#username').keyup(function(ev) { if(ev.keyCode == 13) shareselected(); });

    // user browser (for sample sharing)
    $('#userbrowser').on('show.bs.modal', function(event) {
        // empty the text field and disable autocompletion
        $('#username').val('');
        $('#username').typeahead('destroy');

        // empty recent collaborators list
        $('#recent-collaborators').html('');

        // update autocompletion for the text field and recent collaborators list
        $.ajax({
            url: "/userlist",
            type: "post",
            data: {"mode": "share", "sampleid": sample_id},
            success: function( data ){
                // set up autocompletion
                $('#username').typeahead({
                    minLength: 1,
                    highlight: true
                },
                {
                    name: 'users',
                    source: substringMatcher(data.users),
                    templates: {
                        suggestion: function(data) {
                            return '<div><img src="/static/images/user.png" width="24px" height="24px">' + data + '</div>';
                        }
                    }
                });
                // make recent collaborators list
                if(data.recent.length > 0)
                    $('#recent-collaborators').append('<div>Recent collaborators:<br>&nbsp</div>');
                for(i in data.recent)
                    $('#recent-collaborators').append('<div class="user" data-name="'+data.recent[i]+'"><img src="/static/images/user.png">'+data.recent[i]+'</div>');
                // set up click event
                $('.user').one('click', function(event) {
                   $('#username').val($(this).data('name'));
                   shareselected();
                });
            }
        });
    });

    // once the modal dialog is open, put the cursor in the username field
    $('#userbrowser').on('shown.bs.modal', function(event) { $('#username').focus(); });

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
});