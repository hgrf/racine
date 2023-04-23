import Dialog from './dialog';

class ErrorDialog extends Dialog {
  show(message) {
    this.dialog.find('.modal-body').text(message);
    super.show();
  }
}

export default ErrorDialog;
