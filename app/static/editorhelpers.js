function lightboxwrapper() {
    return '<a class="lightboxlink" href="'+this.src+'?fullsize" data-lightbox="'+sample_id+'">';
}

(function($){   // this is a jQuery plugin
    $.fn.zoombutton = function() {
        $(this).wrap(function() {
            var width = $(this).width() ? $(this).width()+'px' : '100%';   // 100%: workaround for sample image
            return '<div class="imgcontainer" style="width:'+width+'"></div>';
        }).after(function() {
            return '<a class="zoombutton" target="_blank" href="'+$(this).attr('src')+'?fullsize'+'">'+
                   '<i class="glyphicon glyphicon-hd-video" title="Open full resolution in new window"></i></a>'
        });
    };
})(jQuery);
