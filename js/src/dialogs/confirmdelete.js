import $ from 'jquery';

class ConfirmDeleteDialog {
  constructor(callback) {
    const dialog = $('#confirm-delete');
    const okButton = dialog.find('.btn-ok');

    dialog.on('show.bs.modal', function(e) {
      const type = $(e.relatedTarget).data('type');
      const id = $(e.relatedTarget).data('id');
      okButton.data('type', type);
      okButton.attr('id', id);
      $('.debug-id').html(
        `Delete <strong>${type}</strong> ID: <strong>${id}</strong>`,
      );
    });

    okButton.on('click', function(e) {
      const type = okButton.data('type');
      const id = okButton.attr('id');
      callback(type, id);
    });
  }
}

export default ConfirmDeleteDialog;
