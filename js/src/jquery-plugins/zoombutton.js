import jQuery from 'jquery';

(function($) {
  $.fn.zoombutton = function() {
    const elements = $(this); // eslint-disable-line no-invalid-this
    elements.wrap(function() {
      const element = $(this); // eslint-disable-line no-invalid-this
      // 100%: workaround for sample image
      const width = element.width() ? element.width()+'px' : '100%';
      return '<div class="imgcontainer" style="width:'+width+'"></div>';
    }).after(function() {
      const src = $(this).attr('src'); // eslint-disable-line no-invalid-this
      const separator = src.includes('?') ? '&' : '?';
      return (
        `<a class="zoombutton" target="_blank" href="${src}${separator}fullsize">` +
          '<i class="glyphicon glyphicon-hd-video" title="Open full resolution in new window">' +
          '</i>' +
        '</a>'
      );
    });
  };
})(jQuery);
