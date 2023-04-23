import $ from 'jquery';
import Dialog from './dialog';

class ConfirmDeleteDialog extends Dialog {
  constructor(callback) {
    super('#dlg-confirm-delete');

    this.type = null;
    this.id = null;

    this.btnOk = this.dialog.find('.btn-ok');
    this.btnOk.on('click', () => callback(this.type, this.id));

    this.text = this.dialog.find('.debug-id').first();
  }

  onShow(event) {
    this.type = $(event.relatedTarget).data('type');
    this.id = $(event.relatedTarget).data('id');
    this.text.html(`Delete <strong>${this.type}</strong> ID: <strong>${this.id}</strong>`);
  }
}

export default ConfirmDeleteDialog;
