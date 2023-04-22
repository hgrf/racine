import $ from 'jquery';

class UsersView {
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
      location.href = `/settings/users?delete=${id}`;
    });

    $('.loginas').click(function(event) {
      $.ajax({
        url: '/loginas',
        type: 'get',
        data: {'userid': $(this).data('userid')}, // eslint-disable-line no-invalid-this
        success: function(data) {
          location.href = '/';
        },
        error: function(data) {
          alert('Could not login.');
        },
      });
    });

    // set up editables
    $('.txteditable').texteditable();
    $('.cmbeditable').comboeditable({'True': 'True', 'False': 'False'});
    $('.editable').setup_triggers();
  }
}

export default UsersView;
