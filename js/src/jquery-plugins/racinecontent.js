import jQuery from 'jquery';

// polyfill for string startsWith
if (!String.prototype.startsWith) {
  String.prototype.startsWith = function(searchString, position) {
    position = position || 0;
    return this.indexOf(searchString, position) === position;
  };
}

(function($) { // this is a jQuery plugin
  $.fn.racinecontent = function() {
    // catch internal links

    $('a').click(function(event) {
      // N.B. the detection of internal links does not work with Internet Explorer because the href attribute
      // contains the entire address
      // TODO: reduce redundancy with ckeditable.js
      if (typeof $(this).attr('href') == 'string' && $(this).attr('href').startsWith('/sample/')) {
        event.preventDefault();
        R.loadSample($(this).attr('href').split('/')[2]);
      }
    });


    $(this).find('a').click(function(event) {
      if (typeof $(this).attr('href') == 'string' && $(this).attr('href').startsWith('/sample/')) {
        event.preventDefault();
        R.loadSample($(this).attr('href').split('/')[2]);
      }
    });

    // add zoom buttons to images
    $(this).find('img').zoombutton();

    // put lightbox link around images
    $(this).find('img').wrap(R.lightboxWrapper);
  };
})(jQuery);
