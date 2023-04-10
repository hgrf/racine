import "lightbox2";
import "./jquery-plugins/ckeditable";

import * as API from "./api";

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

        if ('view' in this.state) {
            setupBrowserNavigation();

            // figure out what page to load
            this.views[this.state.view].load(true, this.state);
            this.views[this.state.view].onDocumentReady();
        }
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