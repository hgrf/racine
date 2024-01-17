import $ from 'jquery';
import icons from '../../util/icons';

// this function adds a caret to naventry
function addNavCaret(naventry) {
  naventry.prepend(`<i class="nav-caret ${icons.navCaret.common}"></i>`);
  updateNavCaret(naventry);
}

// this function updates the carets as a function of the number of children
function updateNavCaret(naventry) {
  const glyph = naventry.find('i.nav-caret').first();
  const target = $(naventry.data('target'));
  const iconCollapsed = icons.navCaret.collapsed;
  const iconExpanded = icons.navCaret.expanded;

  if (target.children().length > 0) {
    if (target.is(':hidden')) {
      glyph.addClass(iconCollapsed);
    } else {
      glyph.addClass(iconExpanded);
    }

    // change the carets when items are expanded or collapsed
    target.on('show.bs.collapse', function(e) {
      // the event goes up like a bubble and so it can affect parent nav-entries, stop this
      e.stopPropagation();
      glyph.removeClass(iconCollapsed);
      glyph.addClass(iconExpanded);
    });
    target.on('hide.bs.collapse', function(e) {
      e.stopPropagation();
      glyph.addClass(iconCollapsed);
      glyph.removeClass(iconExpanded);
    });
  } else {
    // switch off existing handlers and update classes
    target.off('show.bs.collapse');
    target.off('hide.bs.collapse');
    glyph.removeClass(iconCollapsed);
    glyph.removeClass(iconExpanded);
  }
}

export {addNavCaret, updateNavCaret};
