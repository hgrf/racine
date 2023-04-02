var R;

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
       R.loadSample($(this).data('id'));
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
                url: "/api/set/sample/image/"+sample_id,
                type: "post",
                headers: { 'Authorization': 'Bearer ' + api_token },
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
        R.samplesAPI.toggleArchived(sample_id, function(error, data, response) {
            if (!response)
                error_dialog("Server error. Please check your connection.");
            else if (response.error) {
                if (response.body.message)
                    error_dialog(response.body.message);
                else
                    error_dialog(response.error);
            } else {
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
        R.samplesAPI.toggleCollaborative(sample_id, function(error, data, response) {
            if (!response)
                error_dialog("Server error. Please check your connection.");
            else if (response.error) {
                if (response.body.message)
                    error_dialog(response.body.message);
                else
                    error_dialog(response.error);
            } else {
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
        R.loadSample(sample_id, false, false, false);
    });

    $('#showparentactions').click(function() {
        showparentactions = !showparentactions; // toggle
        R.loadSample(sample_id, false, false, false);
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

        var formdata = {};
        $('#newactionform').serializeArray().map(function(x){formdata[x.name] = x.value;});

        R.actionsAPI.createAction(sample_id, formdata, function(error, data, response) {
            if (!response)
                error_dialog("Server error. Please check your connection.");
            else if (response.error) {
                if (response.body.resubmit) {
                    // form failed validation; because of invalid data or expired CSRF token
                    // we still reload the sample in order to get a new CSRF token, but we
                    // want to keep the text that the user has written in the description field
                    $(document).one("editor_initialised", formdata, function(event) {
                        CKEDITOR.instances.description.setData(event.data.description);
                        error_dialog("Form is not valid. Either you entered an invalid date " +
                                     "or the session has expired. Try submitting again.");
                    });
                } else {
                    error_dialog(response.error);
                    return;
                }
            }

            // reload the sample
            // TODO: it would be sufficient to just add the new action
            // destroy it so that it doesn't bother us with confirmation dialogs when we
            // reload the sample
            CKEDITOR.instances['description'].destroy();
            R.loadSample(sample_id, false, false, false);
        });
    });

    // catch internal links
    $('a').click(function(event) {
        // N.B. the detection of internal links does not work with Internet Explorer because the href attribute
        // contains the entire address
        if(typeof $(this).attr('href') == 'string' && $(this).attr('href').startsWith('/sample/')) {
            event.preventDefault();
            R.loadSample($(this).attr('href').split('/')[2]);
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
        R.actionsAPI.swapActionOrder(
            {'actionid': $(this).data('id'), 'swapid': $(this).data('swapid')},
            function(error, data, response) {
                if (!response)
                    error_dialog("Server error. Please check your connection.");
                else if (response.error) {
                    if (response.body.message)
                        error_dialog(response.body.message);
                    else
                        error_dialog(response.error);
                } else {
                    R.loadSample(sample_id, false, false, false);
                }
        });
    });

    $('.togglenews').click(function(event) {
        var flag_element = $(this);
        var actionid = flag_element.data('id');

        // is this action not yet marked as news?
        if(flag_element.hasClass('markasnews')) {
            // set the action ID hidden field
            // TODO: it seems a bit dangerous that this form field is just called "actionid"
            $('#actionid').val(actionid);
            // clear other fields
            $('#title').val('');
            $('#expires').val('');
            $('#dlg_markasnews').modal('show');
        } else {
            R.actionsAPI.unmarkActionAsNews({ "actionid": actionid }, function(error, data, response) {
                if (!response)
                    error_dialog("Server error. Please check your connection.");
                else if (response.error) {
                    if (response.body.message)
                        error_dialog(response.body.message);
                    else
                        error_dialog(response.error);
                } else {
                    flag_element.removeClass('unmarkasnews');
                    flag_element.addClass('markasnews');
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
            document.title = "Racine";

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
            document.title = "Racine - Search";

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
    R = new Racine(api_token);
});