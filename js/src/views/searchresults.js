import $ from 'jquery';

import BaseView from './base';

class SearchResultsView extends BaseView {
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
