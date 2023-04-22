import './util/jquery-global.js';
import 'bootstrap';
import './typeahead';

import $ from 'jquery';

import 'bootstrap-toc/bootstrap-toc';
import 'lightbox2';
import './jquery-plugins/jquery.jeditable';
import './jquery-plugins/ckeditable';
import './jquery-plugins/zoombutton';
import './jquery-plugins/racinecontent';

import * as API from './api';
import views from './views';

import {createSearchSample} from './util/searchsample';

class Racine {
  constructor(apiToken, view, params) {
    const self = this;

    this.apiToken = apiToken;
    this.apiClient = new API.ApiClient(window.location.origin);
    this.apiClient.authentications['bearerAuth'].accessToken = apiToken;

    this.samplesAPI = new API.SamplesApi(this.apiClient);
    this.sharesAPI = new API.SharesApi(this.apiClient);
    this.actionsAPI = new API.ActionsApi(this.apiClient);

    if (view in views) {
      this.view = new views[view](params);
    } else {
      console.error('Unknown view: ' + view);
      return;
    }

    $(document).ready(function() {
      self.onDocumentReady();
    });
  }

  onDocumentReady() {
    const self = this;
    // login view and browser view do not have a sidebar
    if ((this.view instanceof views.login) || (this.view instanceof views.browser)) {
      this.view.onDocumentReady();
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
      self.mobileHideSidebar();
    });

    $('.nav-button-toggle').click(function() {
      const element = $(this); // eslint-disable-line no-invalid-this
      if (element.hasClass('active')) {
        element.removeClass('active');
      } else {
        element.addClass('active');
      }
    });

    this.#setupHeaderSearch();

    this.view.onDocumentReady();
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
    const id = R.view.state.sampleid;
    if (this.src.includes('?')) {
      return `<a class="lightboxlink" href="${this.src}&fullsize" data-lightbox="${id}">`;
    } else {
      return `<a class="lightboxlink" href="${this.src}?fullsize" data-lightbox="${id}">`;
    }
  }

  #setupHeaderSearch() {
    const self = this;

    createSearchSample($('#navbar-search'));

    $('#navbar-search').bind('typeahead:selected', function(event, suggestion) {
      const field = $(this); // eslint-disable-line no-invalid-this
      field.typeahead('val', ''); // clear the search field
      if (self.view instanceof views.main) {
        self.view.loadSample(suggestion.id);
      } else {
        self.errorDialog('Loading samples is not implemented for this view yet.');
      }
    });

    $('#navbar-search').keypress(function(event) {
      const field = $(this); // eslint-disable-line no-invalid-this
      if (event.which == 13) {
        if (field.val() === '') {
          self.errorDialog('Please specify a search term');
        } else {
          if (self.view instanceof views.main) {
            self.view.loadSearchResults(field.val());
          } else {
            self.errorDialog('Search is not implemented for this view yet.');
          }
          field.typeahead('val', ''); // clear the search field
        }
      }
    });
  }

  makeSamplesClickable() {
    const self = this;

    $('div.sample').click(function() {
      const id = $(this).data('id'); // eslint-disable-line no-invalid-this
      if (self.view instanceof views.main) {
        self.view.loadSample(id);
      } else {
        self.errorDialog('Loading samples is not implemented for this view yet.');
      }
    });
  }
}

export default Racine;
