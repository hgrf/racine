import $ from 'jquery';

class Dialog {
  constructor(selector) {
    this.dialog = $(selector);

    this.dialog.on('show.bs.modal', (event) => this.onShow(event));
    this.dialog.on('shown.bs.modal', (event) => this.onShown(event));
  }

  onShow(event) {
  }

  onShown(event) {
  }
}

export default Dialog;
