import $ from 'jquery';

class SMBResourcesView {
  constructor(params) {
    this.params = params;
  }

  onDocumentReady() {
    $('#confirm-delete').on('show.bs.modal', function(e) {
      const id = $(e.relatedTarget).data('id');
      const okButton = $(this).find('.btn-ok'); // eslint-disable-line no-invalid-this
      okButton.attr('id', id);
      $('.debug-id').html(`Delete ID: <strong>${id}</strong>`);
    });

    $('.btn-ok').click(function(event) {
      const id = $(this).attr('id'); // eslint-disable-line no-invalid-this
      location.href = `/settings/smbresources?delete=${id}`;
    });

    // set up editables
    $('.editable').texteditable();
    $('.editable').setup_triggers();
  }
}

export default SMBResourcesView;
