import $ from 'jquery';

class Dialog {
  constructor(selector) {
    this.dialog = $(selector);

    this.dialog.on('show.bs.modal', (event) => this.onShow(event));
    this.dialog.on('shown.bs.modal', (event) => this.onShown(event));
    this.dialog.on('hide.bs.modal', (event) => this.onHide(event));
  }

  hide() {
    this.dialog.modal('hide');
  }

  show() {
    this.dialog.modal('show');
  }

  onShow(event) {
  }

  onShown(event) {
  }

  onHide(event) {
  }
}

export default Dialog;
