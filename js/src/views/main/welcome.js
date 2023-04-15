import $ from 'jquery';

import MainViewBase from './base';

class WelcomeView extends MainViewBase {
  constructor() {
    super();
  }

  load(pushState, state) {
    if (!super.confirmUnload()) {
      return false;
    }

    $.ajax({
      url: '/welcome',
      success: function(data) {
        R.updateState(pushState, state);

        $('#editor-frame').html(data);
        document.title = 'Racine';
        R.makeSamplesClickable();
      },
    });

    return true;
  }
}

export default WelcomeView;
