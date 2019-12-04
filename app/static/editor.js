var sample_id;
var term;
var hiddeneditor;
var showparentactions = false;

CKEDITOR.timestamp='20191201h';

// polyfill for string startsWith
if (!String.prototype.startsWith) {
  String.prototype.startsWith = function(searchString, position) {
    position = position || 0;
    return this.indexOf(searchString, position) === position;
  };
}

// configure the CKEditor
var ckeditorconfig = {
    extraPlugins: 'save,fb',
    imageUploadUrl: '/browser/upload?type=img',
    uploadUrl: '/browser/upload?type=att',
    filebrowserImageUploadUrl: '/browser/upload?type=img',
    filebrowserLinkUploadUrl: '/browser/upload?type=att',
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

$.ajaxSetup({ cache: false });

function make_samples_clickable() {
    // check if load_sample is defined
    $('div.sample').click(function() {
       load_sample($(this).data('id'));
    });
}

function setup_sample_image() {
    $('#sampleimage').zoombutton();
    $('#sampleimage').wrap(lightboxwrapper);

    // handler for button that changes sample image
    $('#changesampleimage').click(function(event) {
        CKEDITOR.fbtype = 'img';
        CKEDITOR.fbupload = true;
        CKEDITOR.fbcallback = function(url) {
            $.ajax({
                url: "/set/sample/image/"+sample_id,
                type: "post",
                data: { "value": url },
                success: function() {
                    // check if there is currently a sample image
                    if($('#sampleimage').length) {
                        // update the sample image
                        $('#sampleimage').attr('src', url);
                    } else {
                        // add sample image and remove "add sample image" link
                        var div = $('div.newsampleimage');
                        div.removeClass('newsampleimage');
                        div.addClass('imgeditable');
                        div.empty();
                        // TODO: this is duplicated code from templates/editor.html, there is probably a more elegant
                        //       way to sort this out
                        div.append('<img id="sampleimage" src="'+url+'">'+
                                   '<img id="changesampleimage" src="/static/images/insertimage.png"'
                                                             +' title="Change sample image">');
                        setup_sample_image();
                    }
                }
            });
        };
        // use hidden CKEDITOR instance to open the filebrowser dialog
        hiddeneditor.execCommand('fb');
        event.preventDefault();
    });
}

function init_editor(scrolltotop) {
    // define default values for arguments
    var scrolltotop = typeof scrolltotop !== 'undefined' ? scrolltotop : true;
  
    sample_id = $('#sampleid').text();
    if($('#hiddenckeditor').length)     // check if this field exists
        hiddeneditor = CKEDITOR.inline($('#hiddenckeditor')[0], $.extend({'removePlugins': 'toolbar,clipboard,pastetext,pastefromword,tableselection,widget,uploadwidget,pastefromexcel,uploadimage,uploadfile'}, ckeditorconfig));

    // scroll to top
    if(scrolltotop)
        $('html, body').scrollTop(0);

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
        load_sample($('#sampleid').text(), false, false, false);
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
                load_sample(sample_id, false, false, false);
            },
            error: function( jqXHR, textStatus ) {
                error_dialog("Could not connect to the server. Please make sure you are connected and try again.");
            }
        });
    });

    // catch internal links
    $('a').click(function(event) {
        // N.B. the detection of internal links does not work with Internet Explorer because the href attribute
        // contains the entire address
        if(typeof $(this).attr('href') == 'string' && $(this).attr('href').startsWith('/sample/')) {
            event.preventDefault();
            load_sample($(this).attr('href').split('/')[2]);
        }
    });

    // set up the sample image
    setup_sample_image();

    // add zoom buttons to images
    $('#sampledescription').find('img').zoombutton();
    $('.actiondescription').find('img').zoombutton();

    // put lightbox link around images
    $('#sampledescription').find('img').wrap(lightboxwrapper);
    $('.actiondescription').find('img').wrap(lightboxwrapper);

    // typeset all equations
    if(typeof(MathJax) !== 'undefined' && MathJax.isReady)         // if it is not ready now, it should typeset automatically once it is ready
        MathJax.Hub.Queue(["Typeset",MathJax.Hub]);

    // set up CKEditor for new action form
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
                load_sample(sampleid, false, false, false);
            }
        });
    });

    $(document).trigger("editor_initialised");
}

function load_sample(id, pushstate, scrolltotop, scrollnavbar) {
    // define default values for arguments
    var pushstate = typeof pushstate !== 'undefined' ?  pushstate : true;
    var scrolltotop = typeof scrolltotop !== 'undefined' ? scrolltotop : true;
    var scrollnavbar = typeof scrollnavbar !== 'undefined' ? scrollnavbar : true;

    // if currently viewing a sample (not welcome page) then change the navbar background to transparent before loading
    // the new sample (do not do this if the viewed sample is unchanged)
    if($('#sampleid').text() !== "" && $('#sampleid').text() !== id)
        $('#nav-entry' + sample_id).css("background-color", "transparent");

    // load the sample data and re-initialise the editor
    $.ajax({
        url: "/editor/"+id+(showparentactions ? "?showparentactions=1" : ""),
        pushstate: pushstate,
        scrolltotop: scrolltotop,
        scrollnavbar: scrollnavbar,
        success: function( data ) {
            $( "#editor-frame" ).html(data);
            sample_id = $('#sampleid').text();
            if(this.pushstate)
                window.history.pushState({"id": sample_id}, "", "/sample/"+ sample_id);
            document.title = "MSM - "+$('#samplename').text();
            init_editor(this.scrolltotop);
            // highlight in navbar, if the navbar is already loaded
            if($('#nav-entry'+sample_id).length) {
                $('#nav-entry'+sample_id).css("background-color", "#BBBBFF");
                if(scrollnavbar)
                    show_in_navbar(sample_id, false);
            }
        },
        error: function() {
            error_dialog('Sample #'+id+" does not exist or you do not have access to it.");
        }
    });
}

function load_welcome(pushstate) {
    // load welcome page
    $.ajax({
        url: "/welcome",
        success: function(data) {
            // if currently viewing a sample (not welcome page) then change the navbar background to transparent
            if(typeof sample_id !== "undefined")
                $('#nav-entry' + sample_id).css("background-color", "transparent");
            sample_id = undefined;

            if(pushstate)
                window.history.pushState({},"", "/");
            document.title = "Mercury Sample Manager";

            $("#editor-frame").html(data);
            make_samples_clickable();
        }
    });
}

function load_searchresults(term, pushstate) {
    $.ajax({
        url: "/search?ajax=true&term="+term,
        success: function(data) {
            // if currently viewing a sample (not welcome page) then change the navbar background to transparent
            if(typeof sample_id !== "undefined")
                $('#nav-entry' + sample_id).css("background-color", "transparent");
            sample_id = undefined;

            if(pushstate)
                window.history.pushState({"term": term}, "", "/search?term="+term);
            document.title = "MSM - Search";

            $("#editor-frame").html(data);
            make_samples_clickable();
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
            if(typeof e.state.term !== "undefined") {
                load_searchresults(e.state.term, false);
            } else if(typeof e.state.id !== "undefined") {
                load_sample(e.state.id, false, false, true);
            } else {
                load_welcome(false);
            }
        else
            location.href = "/";
    });

    // figure out what page to load
    if(typeof sample !== "undefined") {
        load_sample(sample, true);
    } else if(typeof term !== "undefined") {
        load_searchresults(term, true);
    } else {
        load_welcome(true);
    }

    // add window unload handler (which asks the user to confirm leaving the page when one of the CKEditor instances
    // has been modified
    window.addEventListener('beforeunload', before_unload_handler);

    // set up search field in header bar
    create_searchsample($('#navbar-search'));

    $('#navbar-search').bind('typeahead:selected', function(event, suggestion) {
        $(this).typeahead('val', '');    // clear the search field
        load_sample(suggestion.id);
    });

    $('#navbar-search').keypress(function(event) {
        if (event.which == 13) {
            // if currently viewing a sample (not welcome page) then change the navbar background to transparent
            if(typeof sample_id !== "undefined")
                $('#nav-entry' + sample_id).css("background-color", "transparent");

            if($(this).val() === '') {
                error_dialog('Please specify a search term');
            } else {
                load_searchresults($(this).val(), true);  // load the searchresults page
                $(this).typeahead('val', '');    // clear the search field
            }
        }
    });

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
                switch(type) {
                    case "sample":
                        load_welcome(true);
                        load_navbar(undefined, undefined, false, true);
                        break;
                    case "action":
                        $('#'+id+'.list-entry').remove();
                        break;
                    case "share":
                        $('#sharelistentry'+data.shareid).remove();
                        if(data.code==2) { // if the user removed himself from the sharer list
                            load_welcome(true);
                            load_navbar(undefined, undefined, false, true);
                        }
                        break;
                }
                $('#confirm-delete').modal('hide');
            }
        });
    });
});