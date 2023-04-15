import $ from 'jquery';

import MainViewBase from './base';

class SearchResultsView extends MainViewBase {
  constructor() {
    super();
  }

  load(pushState, state) {
    if (!super.confirmUnload()) {
      return false;
    }

    $.ajax({
      url: '/search?ajax=true&term='+state.term,
      success: function(data) {
        R.updateState(pushState, state);

        $('#editor-frame').html(data);
        document.title = 'Racine - Search';
        R.makeSamplesClickable();
      },
    });

    return true;
  }
}

export default SearchResultsView;
