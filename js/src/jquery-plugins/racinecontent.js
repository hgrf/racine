import jQuery from 'jquery';

(function($) {
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
