import $ from 'jquery';
import ConfirmDeleteDialog from '../dialogs/confirmdelete';

class UsersView {
  constructor(params) {
    this.params = params;
  }

  onDocumentReady() {
    new ConfirmDeleteDialog(function(type, id) {
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
