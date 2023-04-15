import $ from 'jquery';

import {createSelectSample} from '../util/searchsample';

class PrintView {
  constructor() {
    this.state = {};
  }

  load(state) {
    this.state = state;
  }

  onDocumentReady() {
    const images = document.getElementsByTagName('img');
    for (let i=0; i < images.length; i++) {
      images[i].orgwidth = images[i].style.width;
      images[i].orgheight = images[i].style.height;
    }

    $('.dropdown-menu li a').click(function() {
      $('.btn:first-child').html($(this).text()+'<span class="caret"></span>');
      if ($(this).text() == 'Off') {
        for (var i=0; i < images.length; i++) {
          images[i].style.width = images[i].orgwidth;
          images[i].style.height = images[i].orgheight;
        }
      } else {
        for (var i=0; i < images.length; i++) {
          images[i].style.width = $(this).text();
          images[i].style.height = 'auto';
        }
      }
    });

    $('#chkshowuser').on('change', function() {
      const spans = document.getElementsByClassName('username');
      if (document.getElementById('chkshowuser').checked) {
        for (var i = 0; i < spans.length; i++) {
          spans[i].style.display = 'none';
        }
      } else {
        for (var i = 0; i < spans.length; i++) {
          spans[i].style.display = 'initial';
        }
      }
    });

    createSelectSample($('#sample'), $('#sampleid'), !this.state.sampleerror, 'All');

    $('#btnprint').click(function() {
      $('body').append('<div id="printDestination">'+document.getElementById('printArea').innerHTML+'</div>');
      window.print();
      $('#printDestination').remove();
    });
  }
}

export default PrintView;
