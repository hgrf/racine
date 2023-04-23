import $ from 'jquery';

class AjaxView {
  constructor(mainView) {
    this.mainView = mainView;
  }

  load(state, pushState, reload) {
    const self = this;

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
  }

  onDocumentReady() {
  }
}

export default AjaxView;
