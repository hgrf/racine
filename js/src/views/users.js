import $ from 'jquery';
import R from '../racine';
import FormDialog from '../dialogs/formdialog';
import ConfirmDeleteDialog from '../dialogs/confirmdelete';

class NewUserDialog extends FormDialog {
  submit(formdata) {
    R.usersAPI.createUser(formdata, this.apiCallback.bind(this));
  }

  onSuccess(data) {
    location.reload();
  }
}

class UsersView {
  constructor(params) {
    this.params = params;
  }

  onDocumentReady() {
    new NewUserDialog('#dlg-new-user');

    new ConfirmDeleteDialog({'user': (id) => {
      R.usersAPI.deleteUser(id, (error, data, response) => {
        if (!R.responseHasError(response)) {
          location.reload();
        }
      });
    }});

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
