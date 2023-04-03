import * as API from "./api";
import "lightbox2";
import NewSampleDialog from "./dialogs/newsample";
import MarkAsNewsDialog from "./dialogs/markasnews";
import UserBrowserDialog from "./dialogs/userbrowser";
import { loadNavbar, showInNavbar } from "./navbar";

import { pushCurrentState, setupBrowserNavigation } from "./views/base";
import SampleView from "./views/sample";
import SearchResultsView from "./views/searchresults";
import WelcomeView from "./views/welcome";

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
    constructor(apiToken, state) {
        this.apiToken = apiToken;
        this.apiClient = new API.ApiClient(window.location.origin);
        this.apiClient.authentications["bearerAuth"].accessToken = apiToken;

        this.samplesAPI = new API.SamplesApi(this.apiClient);
        this.sharesAPI = new API.SharesApi(this.apiClient);
        this.actionsAPI = new API.ActionsApi(this.apiClient);

        this.views = {
            sample: new SampleView(),
            searchResults: new SearchResultsView(),
            welcome: new WelcomeView(),
        }

        this.state = state;
    }

    updateState(pushState, state) {
        this.state = state;
        if(pushState)
            pushCurrentState();
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

        setupBrowserNavigation();

        // figure out what page to load
        this.views[this.state.view].load(true, this.state);

        // set up search field in header bar
        create_searchsample($('#navbar-search'));

        $('#navbar-search').bind('typeahead:selected', function (event, suggestion) {
            $(this).typeahead('val', '');    // clear the search field
            R.loadSample(suggestion.id);
        });

        $('#navbar-search').keypress(function (event) {
            if (event.which == 13) {
                if ($(this).val() === '') {
                    R.errorDialog('Please specify a search term');
                } else {
                    R.loadSearchResults($(this).val());
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
                            R.loadWelcome();
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
                                R.loadWelcome();
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

    loadSample(id, reload=false) {
        var state = {"view": "sample", "sampleid": id, "url": "/sample/" + id};
        this.views.sample.load(true, state, reload);
    }

    loadSearchResults(query) {
        var state = {"view": "searchResults", "term": query, "url": "/search?term=" + query};
        this.views.searchResults.load(true, state);
    }

    loadWelcome() {
        var state = {"view": "welcome", "url": "/welcome"};
        this.views.welcome.load(true, state);
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
            return '<a class="lightboxlink" href="'+this.src+'&fullsize" data-lightbox="'+R.state.sampleid+'">';
        } else {
            return '<a class="lightboxlink" href="'+this.src+'?fullsize" data-lightbox="'+R.state.sampleid+'">';
        }
    }

    makeSamplesClickable() {
        $('div.sample').click(function() {
            R.loadSample($(this).data('id'));
        });
    }
}

export default Racine;