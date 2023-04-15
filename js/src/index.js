import './util/jquery-global.js';
import 'bootstrap';

import $ from 'jquery';

import typeahead from './typeahead';
typeahead.loadjQueryPlugin();

import 'bootstrap-toc/bootstrap-toc';
import 'lightbox2';
import './jquery-plugins/jquery.jeditable';
import './jquery-plugins/ckeditable';
import './jquery-plugins/zoombutton';
import './jquery-plugins/racinecontent';

import * as API from './api';
import views from './views';

import {pushCurrentState, setupBrowserNavigation} from './views/base';

import {createSearchSample} from './util/searchsample';

class Racine {
  constructor(apiToken, state) {
    this.apiToken = apiToken;
    this.apiClient = new API.ApiClient(window.location.origin);
    this.apiClient.authentications['bearerAuth'].accessToken = apiToken;

    this.samplesAPI = new API.SamplesApi(this.apiClient);
    this.sharesAPI = new API.SharesApi(this.apiClient);
    this.actionsAPI = new API.ActionsApi(this.apiClient);

    this.views = views;

    this.state = state;

    $(document).ready(function() {
      R.onDocumentReady();
    });
  }

  updateState(pushState, state) {
    this.state = state;
    if (pushState) {
      pushCurrentState();
    }
  }

  onDocumentReady() {
    // login view does not have a sidebar
    if ('view' in this.state && this.state.view === 'login') {
      this.views.login.load(this.state);
      this.views.login.onDocumentReady();
      return;
    }

    $('#toggle-sidebar').click(function() {
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

    $('.nav-button-toggle').click(function() {
      if ($(this).hasClass('active')) {
        $(this).removeClass('active');
      } else {
        $(this).addClass('active');
      }
    });

    this.#setupHeaderSearch();

    if ('view' in this.state) {
      if (this.state.view === 'smbresources') {
        this.views.smbresources.load(this.state);
        this.views.smbresources.onDocumentReady();
        return;
      } else if (this.state.view === 'users') {
        this.views.users.load(this.state);
        this.views.users.onDocumentReady();
        return;
      } else if (this.state.view === 'print') {
        this.views.print.load(this.state);
        this.views.print.onDocumentReady();
        return;
      } else if (this.state.view === 'leave') {
        this.views.leave.load(this.state);
        this.views.leave.onDocumentReady();
        return;
      } else if (this.state.view === 'help') {
        this.views.help.load(this.state);
        this.views.help.onDocumentReady();
        return;
      }

      setupBrowserNavigation();

      // figure out what page to load
      this.views[this.state.view].load(true, this.state);
      this.views[this.state.view].onDocumentReady();
    }
  }

  loadSample(id, reload=false) {
    const state = {'view': 'sample', 'sampleid': id, 'url': '/sample/' + id};
    this.views.sample.load(true, state, reload);
  }

  loadSearchResults(query) {
    const state = {'view': 'searchResults', 'term': query, 'url': '/search?term=' + query};
    this.views.searchResults.load(true, state);
  }

  loadWelcome() {
    const state = {'view': 'welcome', 'url': '/welcome'};
    this.views.welcome.load(true, state);
  }

  mobileHideSidebar() {
    $('#toggle-sidebar').removeClass('active');
    $('.sidebar').removeClass('overlay');
    $('.content-overlay').fadeOut();
  }

  errorDialog(message) {
    // TODO: think about uniting this with flash messages
    $('#errordialog').find('.modal-body').text(message);
    $('#errordialog').modal('show');
  }

  lightboxWrapper() {
    if (this.src.includes('?')) {
      return '<a class="lightboxlink" href="'+this.src+'&fullsize" data-lightbox="'+R.state.sampleid+'">';
    } else {
      return '<a class="lightboxlink" href="'+this.src+'?fullsize" data-lightbox="'+R.state.sampleid+'">';
    }
  }

  #setupHeaderSearch() {
    const self = this;

    createSearchSample($('#navbar-search'));

    $('#navbar-search').bind('typeahead:selected', function(event, suggestion) {
      $(this).typeahead('val', ''); // clear the search field
      self.loadSample(suggestion.id);
    });

    $('#navbar-search').keypress(function(event) {
      if (event.which == 13) {
        if ($(this).val() === '') {
          self.errorDialog('Please specify a search term');
        } else {
          self.loadSearchResults($(this).val());
          $(this).typeahead('val', ''); // clear the search field
        }
      }
    });
  }

  makeSamplesClickable() {
    $('div.sample').click(function() {
      R.loadSample($(this).data('id'));
    });
  }
}

export default Racine;
