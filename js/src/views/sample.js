var sample_id;
var hiddeneditor;

CKEDITOR.timestamp='20201114';

// polyfill for string startsWith
if (!String.prototype.startsWith) {
  String.prototype.startsWith = function(searchString, position) {
    position = position || 0;
    return this.indexOf(searchString, position) === position;
  };
}

$.event.props.push('dataTransfer');   // otherwise jQuery event does not have function dataTransfer

$.ajaxSetup({ cache: false });

function make_samples_clickable() {
    // check if load_sample is defined
    $('div.sample').click(function() {
       loadSample($(this).data('id'));
    });
}

function setup_sample_image() {
    $('#sampleimage').zoombutton();
    $('#sampleimage').wrap(R.lightboxWrapper);

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

function initEditor(scrolltotop) {
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
                R.errorDialog("Server error. Please check your connection.");
            else if (response.error) {
                if (response.body.message)
                    R.errorDialog(response.body.message);
                else
                    R.errorDialog(response.error);
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
                R.errorDialog("Server error. Please check your connection.");
            else if (response.error) {
                if (response.body.message)
                    R.errorDialog(response.body.message);
                else
                    R.errorDialog(response.error);
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
        R.showInNavbar(sample_id, true);
    });

    $('#scrolltobottom').click(function() {
       $('html, body').stop().animate({scrollTop: $('div#editor-frame').height()}, 1000);
    });

    $('#invertactionorder').click(function() {
        invertactionorder = !invertactionorder; // toggle
        loadSample(sample_id, false, false, false);
    });

    $('#showparentactions').click(function() {
        showparentactions = !showparentactions; // toggle
        loadSample(sample_id, false, false, false);
    });

    // datepicker
    $("#timestamp").attr("autocomplete", "off");
    $("#timestamp").datepicker({dateFormat: "yy-mm-dd"});

    // handler for new action submit button
    $('#submit').click( function(event) {
        // prevent "normal" submission of form
        event.preventDefault();

        // check if the user is still modifying any actions before submitting the new one
        if(!R.confirmUnload(['description'], "You have been editing the sample description or one or more past " +
                    "actions. Your changes will be lost if you do not save them, are you sure you want to continue?"))
            return;

        // make sure content of editor is transmitted
        CKEDITOR.instances['description'].updateElement();

        var formdata = {};
        $('#newactionform').serializeArray().map(function(x){formdata[x.name] = x.value;});

        R.actionsAPI.createAction(sample_id, formdata, function(error, data, response) {
            if (!response)
                R.errorDialog("Server error. Please check your connection.");
            else if (response.error) {
                if (response.body.resubmit) {
                    // form failed validation; because of invalid data or expired CSRF token
                    // we still reload the sample in order to get a new CSRF token, but we
                    // want to keep the text that the user has written in the description field
                    $(document).one("editor_initialised", formdata, function(event) {
                        CKEDITOR.instances.description.setData(event.data.description);
                        R.errorDialog("Form is not valid. Either you entered an invalid date " +
                                     "or the session has expired. Try submitting again.");
                    });
                } else {
                    R.errorDialog(response.error);
                    return;
                }
            }

            // reload the sample
            // TODO: it would be sufficient to just add the new action
            // destroy it so that it doesn't bother us with confirmation dialogs when we
            // reload the sample
            CKEDITOR.instances['description'].destroy();
            loadSample(sample_id, false, false, false);
        });
    });

    // catch internal links
    $('a').click(function(event) {
        // N.B. the detection of internal links does not work with Internet Explorer because the href attribute
        // contains the entire address
        if(typeof $(this).attr('href') == 'string' && $(this).attr('href').startsWith('/sample/')) {
            event.preventDefault();
            loadSample($(this).attr('href').split('/')[2]);
        }
    });

    // set up the sample image
    setup_sample_image();

    // add zoom buttons to images
    $('#sampledescription').find('img').zoombutton();
    $('.actiondescription').find('img').zoombutton();

    // put lightbox link around images
    $('#sampledescription').find('img').wrap(R.lightboxWrapper);
    $('.actiondescription').find('img').wrap(R.lightboxWrapper);

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
                    R.errorDialog("Server error. Please check your connection.");
                else if (response.error) {
                    if (response.body.message)
                        R.errorDialog(response.body.message);
                    else
                        R.errorDialog(response.error);
                } else {
                    loadSample(sample_id, false, false, false);
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
                    R.errorDialog("Server error. Please check your connection.");
                else if (response.error) {
                    if (response.body.message)
                        R.errorDialog(response.body.message);
                    else
                        R.errorDialog(response.error);
                } else {
                    flag_element.removeClass('unmarkasnews');
                    flag_element.addClass('markasnews');
                }
            });
        }
    });

    $(document).trigger("editor_initialised");
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
    if(!R.confirmUnload())
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
    if(!R.confirmUnload())
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

function loadSample(id, pushstate, scrolltotop, scrollnavbar) {
    // define default values for arguments
    var pushstate = typeof pushstate !== 'undefined' ?  pushstate : true;
    var scrolltotop = typeof scrolltotop !== 'undefined' ? scrolltotop : true;
    var scrollnavbar = typeof scrollnavbar !== 'undefined' ? scrollnavbar : true;

    if(!R.confirmUnload())
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
            document.title = "Racine - "+$('#samplename').text();
            initEditor(this.scrolltotop);
            // highlight in navbar, if the navbar is already loaded
            if($('#nav-entry'+sample_id).length) {
                $('#nav-entry'+sample_id).css("background-color", "#BBBBFF");
                if(scrollnavbar)
                    R.showInNavbar(sample_id, false);
            }
        },
        error: function() {
            R.errorDialog('Sample #'+id+" does not exist or you do not have access to it.");
        }
    });

    return true;
}

export default loadSample;