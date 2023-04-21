import jQuery from 'jquery';

(function($) { // this is a jQuery plugin
  $.fn.zoombutton = function() {
    $(this).wrap(function() {
      // 100%: workaround for sample image
      const width = $(this).width() ? $(this).width()+'px' : '100%';
      return '<div class="imgcontainer" style="width:'+width+'"></div>';
    }).after(function() {
      if (this.src.includes('?')) {
        return (
          `<a class="zoombutton" target="_blank" href="${this.src}&fullsize">` +
            '<i class="glyphicon glyphicon-hd-video" title="Open full resolution in new window">' +
            '</i>' +
          '</a>'
        );
      } else {
        return (
          `<a class="zoombutton" target="_blank" href="${this.src}?fullsize">` +
            '<i class="glyphicon glyphicon-hd-video" title="Open full resolution in new window">' +
            '</i>' +
          '</a>'
        );
      }
    });
  };
})(jQuery);
