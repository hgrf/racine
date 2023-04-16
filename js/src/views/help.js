import $ from 'jquery';

class HelpView {
  constructor() {
    this.state = {};
  }

  load(state) {
    this.state = state;
  }

  onDocumentReady() {
    $('body').attr('data-spy', 'scroll');
    $('body').attr('data-target', '#toc');
  }
}

export default HelpView;
