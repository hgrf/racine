import $ from 'jquery';

import {createSelectSample} from '../util/searchsample';

class PrintView {
  constructor(params) {
    this.params = params;
  }

  onDocumentReady() {
    const images = document.getElementsByTagName('img');
    for (let i=0; i < images.length; i++) {
      images[i].orgwidth = images[i].style.width;
      images[i].orgheight = images[i].style.height;
    }

    $('.dropdown-menu li a').click(function() {
      const text = $(this).text(); // eslint-disable-line no-invalid-this
      $('.btn:first-child').html(text+'<span class="caret"></span>');
      if (text == 'Off') {
        for (let i=0; i < images.length; i++) {
          images[i].style.width = images[i].orgwidth;
          images[i].style.height = images[i].orgheight;
        }
      } else {
        for (let i=0; i < images.length; i++) {
          images[i].style.width = text;
          images[i].style.height = 'auto';
        }
      }
    });

    $('#chkshowuser').on('change', function() {
      const spans = document.getElementsByClassName('username');
      if (document.getElementById('chkshowuser').checked) {
        for (let i = 0; i < spans.length; i++) {
          spans[i].style.display = 'none';
        }
      } else {
        for (let i = 0; i < spans.length; i++) {
          spans[i].style.display = 'initial';
        }
      }
    });

    createSelectSample($('#sample'), $('#sampleid'), !this.params.sampleerror, 'All');

    $('#btnprint').click(function() {
      $('body').append(
          '<div id="printDestination">'+document.getElementById('printArea').innerHTML+'</div>',
      );
      window.print();
      $('#printDestination').remove();
    });
  }
}

export default PrintView;
