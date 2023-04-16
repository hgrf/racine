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
    // login view does not have a sidebar
    if (this.view instanceof views.login) {
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
    if (this.src.includes('?')) {
      return '<a class="lightboxlink" href="'+this.src+'&fullsize" data-lightbox="'+R.view.state.sampleid+'">';
    } else {
      return '<a class="lightboxlink" href="'+this.src+'?fullsize" data-lightbox="'+R.view.state.sampleid+'">';
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
          if (self.view instanceof views.main) {
            self.view.loadSearchResults($(this).val());
          } else {
            self.errorDialog('Search is not implemented for this view yet');
          }
          $(this).typeahead('val', ''); // clear the search field
        }
      }
    });
  }

  makeSamplesClickable() {
    const self = this;

    $('div.sample').click(function() {
      self.loadSample($(this).data('id'));
    });
  }
}

export default Racine;
