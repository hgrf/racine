import $ from 'jquery';

// this function adds a caret to naventry
function addNavCaret(naventry) {
  naventry.prepend('<i class="nav-caret glyphicon"></i>');
  updateNavCaret(naventry);
}

// this function updates the carets as a function of the number of children
function updateNavCaret(naventry) {
  const glyph = naventry.find('i.nav-caret').first();
  const target = $(naventry.data('target'));

  if (target.children().length > 0) {
    if (target.is(':hidden')) {
      glyph.addClass('glyphicon-expand');
    } else {
      glyph.addClass('glyphicon-collapse-down');
    }

    // change the carets when items are expanded or collapsed
    target.on('show.bs.collapse', function(e) {
      // the event goes up like a bubble and so it can affect parent nav-entries, stop this
      e.stopPropagation();
      glyph.removeClass('glyphicon-expand');
      glyph.addClass('glyphicon-collapse-down');
    });
    target.on('hide.bs.collapse', function(e) {
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
  }
}

export {addNavCaret, updateNavCaret};
