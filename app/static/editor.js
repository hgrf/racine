var sample_id;
var term;
var hiddeneditor;
var showparentactions = false;
var invertactionorder = false;

CKEDITOR.timestamp='20201114';

// polyfill for string startsWith
if (!String.prototype.startsWith) {
  String.prototype.startsWith = function(searchString, position) {
    position = position || 0;
    return this.indexOf(searchString, position) === position;
  };
}

// configure the CKEditor
var ckeditorconfig = {
    extraPlugins: 'save,fb,imagerotate',
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

    // handler for collaborative button
    $('#collaborate').click(function() {
        $.ajax({
            url: "/togglecollaborative",
            type: "post",
            data: {"id": sample_id},
            success: function(data) {
                if(data.iscollaborative) {
                    $('#collaborate').attr('title', 'Make non-collaborative');
                    $('#collaborate').attr('src', '/static/images/non-collaborative.png');
                } else {
                    $('#collaborate').attr('title', 'Make collaborative');
                    $('#collaborate').attr('src', '/static/images/collaborative.png');
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

    $('#invertactionorder').click(function() {
        invertactionorder = !invertactionorder; // toggle
        load_sample(sample_id, false, false, false);
    });

    $('#showparentactions').click(function() {
        showparentactions = !showparentactions; // toggle
        load_sample(sample_id, false, false, false);
    });

    // datepicker
    $("#timestamp").attr("autocomplete", "off");
    $("#timestamp").datepicker({dateFormat: "yy-mm-dd"});

    // handler for new action submit button
    $('#submit').click( function(event) {
        // prevent "normal" submission of form
        event.preventDefault();

        // check if the user is still modifying any actions before submitting the new one
        if(!confirm_unload(['description'], "You have been editing the sample description or one or more past " +
                    "actions. Your changes will be lost if you do not save them, are you sure you want to continue?"))
            return;

        // make sure content of editor is transmitted
        CKEDITOR.instances['description'].updateElement();

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
                // reload the sample
                // TODO: it would be sufficient to just add the new action
                CKEDITOR.instances['description'].destroy();     // destroy it so that it doesn't bother us with
                                                                 // confirmation dialogs when we reload the sample
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

    $('.togglenews').click(function(event) {
        var flag_element = $(this);
        var actionid = flag_element.data('id');

        // is this action not yet marked as news?
        if(flag_element.hasClass('markasnews')) {
            // set the action ID hidden field
            // TODO: it seems a bit dangerous that this form field is just called "action_id"
            $('#action_id').val(actionid);
            // clear other fields
            $('#title').val('');
            $('#expires').val('');
            $('#dlg_markasnews').modal('show');
        } else {
            $.ajax({
                url: "/unmarkasnews",
                type: "post",
                data: { "actionid": actionid },
                success: function(data) {
                    if (data.code === 0) {
                        flag_element.removeClass('unmarkasnews');
                        flag_element.addClass('markasnews');
                    } else {
                        error_dialog(data.error);
                    }
                },
                error: function( jqXHR, textStatus ) {
                    error_dialog("Could not connect to the server. Please make sure you are connected and try again.");
                }
            });
        }
    });

    $(document).trigger("editor_initialised");
}

function confirm_unload(ignore, message) {
    var ignore = typeof ignore !== 'undefined' ? ignore : [];
    ignore = ignore.concat(['newsampledescription']);

    // use the before_unload_handler function to check if any CKEditor is being edited
    // if yes, ask the user if he really wants to load a different sample
    confirm_message = before_unload_handler(0, ignore, message);
    if(confirm_message) {
        if (!confirm(confirm_message)) {
            return false;
        }
    }
    // destroy CKEditors
    for(var i in CKEDITOR.instances) {
        if(ignore.indexOf(i) < 0) {
            CKEDITOR.instances[i].destroy()
        }
    }
    return true;
}

function push_current_state() {
    // figure out what page we currently have and push state accordingly
    if(typeof sample_id !== "undefined") {
        window.history.pushState({"id": sample_id}, "", "/sample/"+sample_id);
    } else if(typeof term !== "undefined") {
        window.history.pushState({"term": term}, "", "/search?term="+term);
    } else {
        window.history.pushState({},"", "/");
    }
}

function load_sample(id, pushstate, scrolltotop, scrollnavbar) {
    // define default values for arguments
    var pushstate = typeof pushstate !== 'undefined' ?  pushstate : true;
    var scrolltotop = typeof scrolltotop !== 'undefined' ? scrolltotop : true;
    var scrollnavbar = typeof scrollnavbar !== 'undefined' ? scrollnavbar : true;

    if(!confirm_unload())
        return false;

    // if currently viewing a sample (not welcome page) then change the navbar background to transparent before loading
    // the new sample (do not do this if the viewed sample is unchanged)
    if(typeof sample_id !== 'undefined' && sample_id !== id)
        $('#nav-entry' + sample_id).css("background-color", "transparent");

    // load the sample data and re-initialise the editor
    $.ajax({
        url: "/editor/"+id+"?invertactionorder="+invertactionorder+"&showparentactions="+showparentactions,
        pushstate: pushstate,
        scrolltotop: scrolltotop,
        scrollnavbar: scrollnavbar,
        success: function( data ) {
            $( "#editor-frame" ).html(data);
            sample_id = $('#sampleid').text();
            term = undefined;
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

    return true;
}

function load_welcome(pushstate) {
    if(!confirm_unload())
        return false;

    // load welcome page
    $.ajax({
        url: "/welcome",
        success: function(data) {
            // if currently viewing a sample (not welcome page) then change the navbar background to transparent
            if(typeof sample_id !== "undefined")
                $('#nav-entry' + sample_id).css("background-color", "transparent");
            sample_id = undefined;
            term = undefined;

            if(pushstate)
                window.history.pushState({},"", "/");
            document.title = "Mercury Sample Manager";

            $("#editor-frame").html(data);
            make_samples_clickable();
        }
    });

    return true;
}

function load_searchresults(term, pushstate) {
    if(!confirm_unload())
        return false;

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

    return true;
}

function before_unload_handler(event, ignore, message) {
    var ignore = typeof ignore !== 'undefined' ? ignore : [];
    var msg = typeof message !== 'undefined' ? message : "Are you sure you want to leave before saving modifications?"

    for(var i in CKEDITOR.instances) {
        // first check if the editor is not on the ignore list
        if(ignore.indexOf(i) < 0 && CKEDITOR.instances[i].checkDirty()) {
            event.returnValue = msg;     // Gecko, Trident, Chrome 34+
            return msg;                  // Gecko, WebKit, Chrome <34
        }
    }
}

$(document).ready(function() {
    // Switch of automatic scroll restoration...
    // so that, if a popstate event occurs but the user does not want to leave the page, automatic scrolling to the top
    // is avoided. However, this means that if we navigate back to some page that was previously scrolled to a specific
    // location, we lose this information and the page is opened at 0 scroll position. This could be solved e.g. by
    // storing the scroll position in the history state variable.
    if ('scrollRestoration' in history) {
        history.scrollRestoration = 'manual';
    }
    // add event handler for history
    window.addEventListener("popstate", function(event) {
        if(event.state != null) {
            var res;
            if(typeof event.state.term !== "undefined") {
                res = load_searchresults(event.state.term, false);
            } else if (typeof event.state.id !== "undefined") {
                res = load_sample(event.state.id, false, false, true);
            } else {
                res = load_welcome(false);
            }
            if(!res)  // the user wants to stay on the page to make modifications
                push_current_state();
        }
        else
            location.href = "/";
    });

    // figure out what page to load
    if(typeof sample_id !== "undefined") {
        load_sample(sample_id, true);
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

    // new sample dialog
    var newsampleparent = $('#newsampleparent');
    var newsampleparentid = $('#newsampleparentid')
    create_selectsample(newsampleparent, newsampleparentid);
    CKEDITOR.replace( 'newsampledescription', ckeditorconfig);

    $('#newsample').on('show.bs.modal', function(event) {
        // set the parent field to the current sample
        if(typeof sample_id !== 'undefined') {
            $('#newsampleparent').typeahead('val', $('#samplename').text());
            $('#newsampleparentid').val(sample_id);
        }
    });

    $('#newsample').on('shown.bs.modal', function() {
        // workaround for a bug in CKEditor -> if we don't do this after the editor is shown, a <br /> tag is inserted
        // if we tab to the editor
        CKEDITOR.instances['newsampledescription'].setData('');

        // put the cursor in the sample name field
        $('#newsamplename').focus();
    });

    $('#newsample').on('hide.bs.modal', function() {
        // clear the dialog
        $('#newsampleclear').trigger('click');
    });

    $('#newsampleclear').click(function(event) {
        event.preventDefault();

        $('#newsamplename').val('');
        newsampleparent.typeahead('val', '');
        newsampleparent.markvalid();
        newsampleparentid.val('');
        CKEDITOR.instances['newsampledescription'].setData('');
    });
    $('#newsamplesubmit').click(function(event) {
        event.preventDefault();

        var newsampleform = $('#newsampleform');

        // clean up error messages
        newsampleform.find('.form-group').removeClass('has-error');
        newsampleform.find('span.help-block').remove();

        // make sure content of editor is transmitted
        CKEDITOR.instances['newsampledescription'].updateElement();

        $.ajax({
            url: "/newsample",
            type: "post",
            data: newsampleform.serialize(),
            success: function(data) {
                if (data.code === 0) {
                    $('#newsample').modal('hide');  // hide and clear the dialog
                    load_sample(data.sampleid);
                    load_navbar();
                } else {
                    console.log(data.error);
                    // form failed validation; because of invalid data or expired CSRF token
                    for(field in data.error) {
                        if(field === 'csrf_token') {
                            error_dialog('The CSRF token has expired. Please reload the page to create a new sample.');
                            continue;
                        }
                        // get form group
                        var formgroupid = (field !== 'newsampleparentid' ? field : 'newsampleparent');
                        var formgroup = $('#'+formgroupid).closest('.form-group');
                        // add the has-error to the form group
                        formgroup.addClass('has-error')
                        // add the error message to the form group
                        for(i in data.error[field]) {
                            formgroup.append('<span class="help-block">'+data.error[field][i]+'</span>');
                        }
                    }
                }
            },
            error: function( jqXHR, textStatus ) {
                error_dialog("Could not connect to the server. Please make sure you are connected and try again.");
            }
        });
    });

    // "mark as news" dialog
    $('#dlg_markasnews_submit').click(function(event) {
        event.preventDefault();

        var dlg_markasnews_form = $('#dlg_markasnews_form');
        var actionid = $("#action_id").val();
        var flag_element = $('#togglenews-' + actionid);

        // clean up error messages
        dlg_markasnews_form.find('.form-group').removeClass('has-error');
        dlg_markasnews_form.find('span.help-block').remove();

        $.ajax({
            url: "/markasnews",
            type: "post",
            data: dlg_markasnews_form.serialize(),
            success: function(data) {
                if (data.code === 0) {
                    // hide the dialog
                    $('#dlg_markasnews').modal('hide');

                    // toggle the flag
                    flag_element.removeClass('markasnews');
                    flag_element.addClass('unmarkasnews');
                } else {
                    console.log(data.error);
                    // form failed validation; because of invalid data or expired CSRF token
                    for(field in data.error) {
                        if(field === 'csrf_token') {
                            error_dialog('The CSRF token has expired. Please reload the page.');
                            continue;
                        }
                        // get form group
                        var formgroup = $('#'+field).closest('.form-group');
                        // add the has-error to the form group
                        formgroup.addClass('has-error')
                        // add the error message to the form group
                        for(i in data.error[field]) {
                            formgroup.append('<span class="help-block">'+data.error[field][i]+'</span>');
                        }
                    }
                }
            },
            error: function( jqXHR, textStatus ) {
                error_dialog("Could not connect to the server. Please make sure you are connected and try again.");
            }
        });
    });

    // datepicker
    $("#expires").attr("autocomplete", "off");
    $("#expires").datepicker({dateFormat: "yy-mm-dd"});

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
            url: "/api/"+type+"/"+id,
            type: "delete",
            beforeSend: function (xhr) {
                xhr.setRequestHeader ("Authorization", "Bearer " + api_token);
            },
            success: function( data, textStatus, jqXHR ) {
                switch(type) {
                    case "action":
                        $('#'+id+'.list-entry').remove();
                        break;
                    case "sample":
                        load_welcome(true);
                        load_navbar(undefined, undefined, false, true);
                        break;
                    case "share":
                        $('#sharelistentry'+data.shareid).remove();
                        if(jqXHR.status == 205) { // if the user removed himself from the sharer list
                            load_welcome(true);
                            load_navbar(undefined, undefined, false, true);
                        }
                        break;
                }
                $('#confirm-delete').modal('hide');
            },
            error: function( jqXHR, textStatus ) {
                error_dialog("Failed to execute request: "+jqXHR.responseText);
            }
        })
    });
});