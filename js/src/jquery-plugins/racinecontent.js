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
    const elements = $(this); // eslint-disable-line no-invalid-this

    // catch internal links
    elements.find('a').click(function(event) {
      const href = $(this).attr('href'); // eslint-disable-line no-invalid-this
      // N.B. the detection of internal links does not work with Internet Explorer because the href
      // attribute contains the entire address
      if (typeof href == 'string' && href.startsWith('/sample/')) {
        event.preventDefault();
        R.view.loadSample(href.split('/')[2]);
      }
    });

    // add zoom buttons to images
    elements.find('img').zoombutton();

    // put lightbox link around images
    elements.find('img').wrap(R.lightboxWrapper);
  };
})(jQuery);
