import * as API from "./api";
import "lightbox2";
import NewSampleDialog from "./dialogs/newsample";
import MarkAsNewsDialog from "./dialogs/markasnews";
import UserBrowserDialog from "./dialogs/userbrowser";
import { loadNavbar, showInNavbar } from "./navbar";
import loadSample from "./views/sample";

(function($){   // this is a jQuery plugin
    $.fn.zoombutton = function() {
        $(this).wrap(function() {
            var width = $(this).width() ? $(this).width()+'px' : '100%';   // 100%: workaround for sample image
            return '<div class="imgcontainer" style="width:'+width+'"></div>';
        }).after(function() {
            if(this.src.includes('?')) {
                return '<a class="zoombutton" target="_blank" href="'+this.src+'&fullsize'+'">'+
                       '<i class="glyphicon glyphicon-hd-video" title="Open full resolution in new window"></i></a>'
            } else {
                return '<a class="zoombutton" target="_blank" href="'+this.src+'?fullsize'+'">'+
                       '<i class="glyphicon glyphicon-hd-video" title="Open full resolution in new window"></i></a>'
            }
        });
    };
})(jQuery);

class Racine {
    constructor(apiToken) {
        this.apiClient = new API.ApiClient(window.location.origin);
        this.apiClient.authentications["bearerAuth"].accessToken = apiToken;

        this.samplesAPI = new API.SamplesApi(this.apiClient);
        this.sharesAPI = new API.SharesApi(this.apiClient);
        this.actionsAPI = new API.ActionsApi(this.apiClient);
    }

    onDocumentReady() {
        $('#toggle-sidebar').click(function () {
            if ($('.sidebar').hasClass('overlay')) {
                $('.sidebar').removeClass('overlay');
                $('.content-overlay').fadeOut();
            } else {
                $('.sidebar').addClass('overlay');
                $('.content-overlay').fadeIn();
            }
        });
    
        $('.content-overlay').click(function() {
            this.mobileHideSidebar();
        });
    
        $('.nav-button-toggle').click(function () {
            if ($(this).hasClass('active')) {
                $(this).removeClass('active');
            } else {
                $(this).addClass('active');
            }
        });

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
                    res = loadSample(event.state.id, false, false, true);
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
            loadSample(sample_id, true);
        } else if (typeof term !== "undefined") {
            load_searchresults(term, true);
        } else {
            load_welcome(true);
        }

        // add window unload handler (which asks the user to confirm leaving the page when one of the CKEditor instances
        // has been modified
        window.addEventListener('beforeunload', this.beforeUnloadHandler);

        // set up search field in header bar
        create_searchsample($('#navbar-search'));

        $('#navbar-search').bind('typeahead:selected', function (event, suggestion) {
            $(this).typeahead('val', '');    // clear the search field
            loadSample(suggestion.id);
        });

        $('#navbar-search').keypress(function (event) {
            if (event.which == 13) {
                // if currently viewing a sample (not welcome page) then change the navbar background to transparent
                if (typeof sample_id !== "undefined")
                    $('#nav-entry' + sample_id).css("background-color", "transparent");

                if ($(this).val() === '') {
                    R.errorDialog('Please specify a search term');
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
                            load_welcome(true);
                            loadNavbar(undefined, undefined, false, true);
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

    mobileHideSidebar() {
        $('#toggle-sidebar').removeClass('active');
        $('.sidebar').removeClass('overlay');
        $('.content-overlay').fadeOut();
    }

    errorDialog(message) {
        // TODO: think about uniting this with flash messages
        $("#errordialog").find(".modal-body").text(message);
        $("#errordialog").modal("show");
    }

    lightboxWrapper() {
        if(this.src.includes('?')) {
            return '<a class="lightboxlink" href="'+this.src+'&fullsize" data-lightbox="'+sample_id+'">';
        } else {
            return '<a class="lightboxlink" href="'+this.src+'?fullsize" data-lightbox="'+sample_id+'">';
        }
    }

    beforeUnloadHandler(event, ignore, message) {
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

    confirmUnload(ignore, message) {
        var ignore = typeof ignore !== 'undefined' ? ignore : [];
        ignore = ignore.concat(['newsampledescription']);
    
        // use the beforeUnloadHandler function to check if any CKEditor is being edited
        // if yes, ask the user if he really wants to load a different sample
        var confirm_message = this.beforeUnloadHandler(0, ignore, message);
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
}

export default Racine;