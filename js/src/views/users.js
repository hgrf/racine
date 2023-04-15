import $ from 'jquery';

class UsersView {
  constructor() {
    this.state = {};
  }

  load(state) {
    this.state = state;
  }

  onDocumentReady() {
    $('#confirm-delete').on('show.bs.modal', function(e) {
      $(this).find('.btn-ok').attr('id', $(e.relatedTarget).data('id'));
      $('.debug-id').html('Delete ID: <strong>' + $(this).find('.btn-ok').attr('id') + '</strong>');
    });

    $('.btn-ok').click(function(event) {
      const id = $(this).attr('id');
      location.href = '/settings/users?delete='+id;
    });

    $('.loginas').click(function(event) {
      $.ajax({
        url: '/loginas',
        type: 'get',
        data: {'userid': $(this).data('userid')},
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
