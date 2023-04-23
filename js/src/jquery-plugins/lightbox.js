import jQuery from 'jquery';

(function($) {
  $.fn.lightbox = function() {
    const elements = $(this); // eslint-disable-line no-invalid-this
    const id = R.view.state.sampleid;
    elements.wrap(function() {
      const src = this.src; // eslint-disable-line no-invalid-this
      const sep = src.includes('?') ? '&' : '?';
      return `<a class="lightboxlink" href="${src}${sep}fullsize" data-lightbox="${id}">`;
    });
  };
})(jQuery);
