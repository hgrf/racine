import $ from 'jquery';

// this function adds a glyphicon to naventry
function addGlyphicon(naventry) {
    naventry.prepend('<i class="glyphicon"></i>');
    updateGlyphicon(naventry);
}

// this function updates the glyphicon as a function of the number of children
function updateGlyphicon(naventry) {
    let glyph = naventry.find('i.glyphicon').first();
    let target = $(naventry.data('target'));

    if (target.children().length > 0) {
        glyph.removeClass('glyphicon-invisible');
        if (target.is(':hidden'))
            glyph.addClass('glyphicon-expand');
        else
            glyph.addClass('glyphicon-collapse-down');

        // change the glyphicons when items are expanded or collapsed
        target.on("show.bs.collapse", function (e) {
            // the event goes up like a bubble and so it can affect parent nav-entries, stop this
            e.stopPropagation();
            glyph.removeClass('glyphicon-expand');
            glyph.addClass('glyphicon-collapse-down');
        });
        target.on("hide.bs.collapse", function (e) {
            e.stopPropagation();
            glyph.addClass('glyphicon-expand');
            glyph.removeClass('glyphicon-collapse-down');
        });
    } else {
        // switch off existing handlers and update classes
        target.off('show.bs.collapse');
        target.off('hide.bs.collapse');
        glyph.removeClass('glyphicon-expand');
        glyph.removeClass('glyphicon-collapse-down');
        glyph.addClass('glyphicon-invisible');
    }
}

export { addGlyphicon, updateGlyphicon };