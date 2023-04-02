import * as API from "./api";
import "lightbox2";
import NewSampleDialog from "./dialogs/newsample";
import MarkAsNewsDialog from "./dialogs/markasnews";
import UserBrowserDialog from "./dialogs/userbrowser";
import { loadNavbar, showInNavbar } from "./navbar";

class Racine {
    constructor(apiToken) {
        this.apiClient = new API.ApiClient(window.location.origin);
        this.apiClient.authentications["bearerAuth"].accessToken = apiToken;

        this.samplesAPI = new API.SamplesApi(this.apiClient);
        this.sharesAPI = new API.SharesApi(this.apiClient);
        this.actionsAPI = new API.ActionsApi(this.apiClient);

        // Switch of automatic scroll restoration...
        // so that, if a popstate event occurs but the user does not want to leave the page, automatic scrolling to the top
        // is avoided. However, this means that if we navigate back to some page that was previously scrolled to a specific
        // location, we lose this information and the page is opened at 0 scroll position. This could be solved e.g. by
        // storing the scroll position in the history state variable.
        if ('scrollRestoration' in history) {
            history.scrollRestoration = 'manual';
        }
        // add event handler for history
        window.addEventListener("popstate", function (event) {
            if (event.state != null) {
                var res;
                if (typeof event.state.term !== "undefined") {
                    res = load_searchresults(event.state.term, false);
                } else if (typeof event.state.id !== "undefined") {
                    res = R.loadSample(event.state.id, false, false, true);
                } else {
                    res = load_welcome(false);
                }
                if (!res)  // the user wants to stay on the page to make modifications
                    push_current_state();
            }
            else
                location.href = "/";
        });

        // figure out what page to load
        if (typeof sample_id !== "undefined") {
            this.loadSample(sample_id, true);
        } else if (typeof term !== "undefined") {
            load_searchresults(term, true);
        } else {
            load_welcome(true);
        }

        // add window unload handler (which asks the user to confirm leaving the page when one of the CKEditor instances
        // has been modified
        window.addEventListener('beforeunload', before_unload_handler);

        // set up search field in header bar
        create_searchsample($('#navbar-search'));

        $('#navbar-search').bind('typeahead:selected', function (event, suggestion) {
            $(this).typeahead('val', '');    // clear the search field
            R.loadSample(suggestion.id);
        });

        $('#navbar-search').keypress(function (event) {
            if (event.which == 13) {
                // if currently viewing a sample (not welcome page) then change the navbar background to transparent
                if (typeof sample_id !== "undefined")
                    $('#nav-entry' + sample_id).css("background-color", "transparent");

                if ($(this).val() === '') {
                    error_dialog('Please specify a search term');
                } else {
                    load_searchresults($(this).val(), true);  // load the searchresults page
                    $(this).typeahead('val', '');    // clear the search field
                }
            }
        });

        // new sample dialog
        new NewSampleDialog('#newsample');

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
                            error_dialog("Server error. Please check your connection.");
                        else if (response.error) {
                            if (response.body.message)
                                error_dialog(response.body.message);
                            else
                                error_dialog(response.error);
                        } else {
                            $('#' + id + '.list-entry').remove();
                        }
                        $('#confirm-delete').modal('hide');
                    });
                    break;
                case "sample":
                    R.samplesAPI.deleteSample(id, function (error, data, response) {
                        if (!response)
                            error_dialog("Server error. Please check your connection.");
                        else if (response.error) {
                            if (response.body.message)
                                error_dialog(response.body.message);
                            else
                                error_dialog(response.error);
                        } else {
                            load_welcome(true);
                            loadNavbar(undefined, undefined, false, true);
                        }
                        $('#confirm-delete').modal('hide');
                    });
                    break;
                case "share":
                    R.sharesAPI.deleteShare(id, function (error, data, response) {
                        if (!response)
                            error_dialog("Server error. Please check your connection.");
                        else if (response.error) {
                            if (response.body.message)
                                error_dialog(response.body.message);
                            else
                                error_dialog(response.error);
                        } else {
                            $('#sharelistentry' + id).remove();
                            if (response.status == 205) { // if the user removed himself from the sharer list
                                load_welcome(true);
                                loadNavbar(undefined, undefined, false, true);
                            }
                            $('#confirm-delete').modal('hide');
                        }
                    });
                    break;
            }
        });

        this.showInNavbar = showInNavbar;

        order = 'id';
        showarchived = false;
    
        // default load with order by ID and hide archived samples
        loadNavbar(order, false);
    }

    loadSample(id, pushstate, scrolltotop, scrollnavbar) {
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
                document.title = "Racine - "+$('#samplename').text();
                init_editor(this.scrolltotop);
                // highlight in navbar, if the navbar is already loaded
                if($('#nav-entry'+sample_id).length) {
                    $('#nav-entry'+sample_id).css("background-color", "#BBBBFF");
                    if(scrollnavbar)
                        showInNavbar(sample_id, false);
                }
            },
            error: function() {
                error_dialog('Sample #'+id+" does not exist or you do not have access to it.");
            }
        });
    
        return true;
    }
}

export default Racine;