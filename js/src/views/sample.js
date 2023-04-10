import MainView from "./main";

import MarkAsNewsDialog from "../dialogs/markasnews";
import UserBrowserDialog from "../dialogs/userbrowser";

import ckeditorconfig from '../util/ckeditorconfig';

/* Disable caching for AJAX requests.
 * This fixes a bug in Internet Explorer, e.g. when reloading the sample
 * after adding an action, the new action is not shown / when modifying an
 * action, the old action is shown after saving, even though the data has
 * been updated on the server.
 * 
 * c.f. https://www.itworld.com/article/2693447/ajax-requests-not-executing
-or-updating-in-internet-explorer-solution.html
 */
$.ajaxSetup({ cache: false });

class SampleView extends MainView {
    constructor() {
        super();
    }

    onDocumentReady() {
        super.onDocumentReady();

        // "mark as news" dialog
        new MarkAsNewsDialog();

        // user browser dialog
        new UserBrowserDialog();

        // sample and action deletion
        $('#confirm-delete').on('show.bs.modal', function (e) {
            $(this).find('.btn-ok').attr('id', $(e.relatedTarget).data('id'));
            $(this).find('.btn-ok').data('type', $(e.relatedTarget).data('type'));
            $('.debug-id').html('Delete <strong>' + $(e.relatedTarget).data('type') + '</strong> ID: <strong>' + $(this).find('.btn-ok').attr('id') + '</strong>');
        });

        $('.btn-ok').click(function (event) {
            var type = $(this).data('type');
            var id = $(this).attr('id');

            switch (type) {
                case "action":
                    R.actionsAPI.deleteAction(id, function (error, data, response) {
                        if (!response)
                            R.errorDialog("Server error. Please check your connection.");
                        else if (response.error) {
                            if (response.body.message)
                                R.errorDialog(response.body.message);
                            else
                                R.errorDialog(response.error);
                        } else {
                            $('#' + id + '.list-entry').remove();
                        }
                        $('#confirm-delete').modal('hide');
                    });
                    break;
                case "sample":
                    R.samplesAPI.deleteSample(id, function (error, data, response) {
                        if (!response)
                            R.errorDialog("Server error. Please check your connection.");
                        else if (response.error) {
                            if (response.body.message)
                                R.errorDialog(response.body.message);
                            else
                                R.errorDialog(response.error);
                        } else {
                            R.loadWelcome();
                        }
                        $('#confirm-delete').modal('hide');
                    });
                    break;
                case "share":
                    R.sharesAPI.deleteShare(id, function (error, data, response) {
                        if (!response)
                            R.errorDialog("Server error. Please check your connection.");
                        else if (response.error) {
                            if (response.body.message)
                                R.errorDialog(response.body.message);
                            else
                                R.errorDialog(response.error);
                        } else {
                            $('#sharelistentry' + id).remove();
                            if (response.status == 205) { // if the user removed himself from the sharer list
                                R.loadWelcome();
                            }
                            $('#confirm-delete').modal('hide');
                        }
                    });
                    break;
            }
        });
    }

    load(pushState, state, reload=false) {
        var sampleid = state.sampleid;
    
        if(!super.confirmUnload())
            return false;
    
        // load the sample data and re-initialise the editor
        $.ajax({
            url: "/editor/"+sampleid+"?invertactionorder="+invertactionorder+"&showparentactions="+showparentactions,
            success: function( data ) {
                if(!reload)
                    R.updateState(pushState, state);

                $( "#editor-frame" ).html(data);
                document.title = "Racine - "+$('#samplename').text();
                if(!reload)
                    $('html, body').scrollTop(0);
                initEditor();
                // highlight in navbar, if the navbar is already loaded
                if($('#nav-entry'+sampleid).length) {
                    $('#nav-entry'+sampleid).css("background-color", "#BBBBFF");
                    if(!reload)
                        MainView.tree.highlight(sampleid, false);
                }
            },
            error: function() {
                R.errorDialog('Sample #'+sampleid+" does not exist or you do not have access to it.");
            }
        });
    
        return true;
    }    
}

var hiddeneditor;

function setup_sample_image() {
    $('#sampleimage').zoombutton();
    $('#sampleimage').wrap(R.lightboxWrapper);

    // handler for button that changes sample image
    $('#changesampleimage').click(function(event) {
        CKEDITOR.fbtype = 'img';
        CKEDITOR.fbupload = true;
        CKEDITOR.fbcallback = function(url) {
            $.ajax({
                url: `/api/set/sample/image/${R.state.sampleid}`,
                type: "post",
                headers: { 'Authorization': 'Bearer ' + R.apiToken },
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

function initEditor() {
    if($('#hiddenckeditor').length)     // check if this field exists
        hiddeneditor = CKEDITOR.inline($('#hiddenckeditor')[0], $.extend({'removePlugins': 'toolbar,clipboard,pastetext,pastefromword,tableselection,widget,uploadwidget,pastefromexcel,uploadimage,uploadfile'}, ckeditorconfig));

    // handler for archive button
    $('#archive').click(function() {
        R.samplesAPI.toggleArchived(R.state.sampleid, function(error, data, response) {
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
                    $(`#nav-entry${R.state.sampleid}`).addClass('nav-entry-archived');
                } else {
                    $('#archive').attr('title', 'Archive');
                    $('#archive').attr('src', '/static/images/archive.png');
                    $(`#nav-entry${R.state.sampleid}`).removeClass('nav-entry-archived');
                }
            }
        });
    });

    // handler for collaborative button
    $('#collaborate').click(function() {
        R.samplesAPI.toggleCollaborative(R.state.sampleid, function(error, data, response) {
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
        MainView.tree.highlight(R.state.sampleid, true);
    });

    $('#scrolltobottom').click(function() {
       $('html, body').stop().animate({scrollTop: $('div#editor-frame').height()}, 1000);
    });

    $('#invertactionorder').click(function() {
        invertactionorder = !invertactionorder; // toggle
        R.loadSample(R.state['sampleid'], true);
    });

    $('#showparentactions').click(function() {
        showparentactions = !showparentactions; // toggle
        R.loadSample(R.state['sampleid'], true);
    });

    // datepicker
    $("#timestamp").attr("autocomplete", "off");
    $("#timestamp").datepicker({dateFormat: "yy-mm-dd"});

    // handler for new action submit button
    $('#submit').click( function(event) {
        // prevent "normal" submission of form
        event.preventDefault();

        // check if the user is still modifying any actions before submitting the new one
        if(!R.views['sample'].confirmUnload(['description'], "You have been editing the sample description or one or more past " +
                    "actions. Your changes will be lost if you do not save them, are you sure you want to continue?"))
            return;

        // make sure content of editor is transmitted
        CKEDITOR.instances['description'].updateElement();

        var formdata = {};
        $('#newactionform').serializeArray().map(function(x){formdata[x.name] = x.value;});

        R.actionsAPI.createAction(R.state['sampleid'], formdata, function(error, data, response) {
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
            R.loadSample(R.state['sampleid'], true);
        });
    });

    // set up the sample image
    setup_sample_image();

    $('#sampledescription').racinecontent();
    $('.actiondescription').racinecontent();


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
            $(`#nav-entry${R.state.sampleid} > .nav-entry-name`).html(data.value);
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
                    R.loadSample(R.state['sampleid'], true);
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

export default SampleView;