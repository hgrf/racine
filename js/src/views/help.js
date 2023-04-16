import $ from 'jquery';

class HelpView {
  constructor(params) {
    this.params = params;
  }

  onDocumentReady() {
    $('body').attr('data-spy', 'scroll');
    $('body').attr('data-target', '#toc');
  }
}

export default HelpView;
