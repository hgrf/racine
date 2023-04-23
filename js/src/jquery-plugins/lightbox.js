import jQuery from 'jquery';

(function($) {
  $.fn.lightbox = function() {
    const elements = $(this); // eslint-disable-line no-invalid-this
    const id = R.view.state.sampleid;
    elements.wrap(function() {
      const sep = this.src.includes('?') ? '&' : '?';
      return `<a class="lightboxlink" href="${this.src}${sep}fullsize" data-lightbox="${id}">`;
    });
  };
})(jQuery);
