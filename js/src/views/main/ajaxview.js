import $ from 'jquery';
import R from '../../racine';

class AjaxView {
  constructor(mainView) {
    this.mainView = mainView;
  }

  load(state, pushState, reload) {
    const self = this;

    $('#editor-frame').html('<div class="loader"></div>');

    $.ajax({
      url: state.url,
      success: function(data) {
        $('#editor-frame').html(data);
        if (!reload) {
          self.mainView.state = state;
          if (pushState) {
            self.mainView.pushCurrentState();
          }
          $('html, body').scrollTop(0);
        }
        self.onLoadSuccess(state, reload);
      },
      error: function(jqXHR, textStatus, error) {
        self.onLoadError(state);
      },
    });
  }

  confirmUnload(ajax=true) {
    return true;
  }

  onLoadSuccess(state, reload) {
  }

  onLoadError(state, jqXHR) {
    R.errorDialog(`Error loading ${state.ajaxView} view.`);
  }

  onDocumentReady() {
  }
}

export default AjaxView;
