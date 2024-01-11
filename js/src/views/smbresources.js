import $ from 'jquery';
import R from '../racine';
import FormDialog from '../dialogs/formdialog';
import ConfirmDeleteDialog from '../dialogs/confirmdelete';

class NewSMBResourceDialog extends FormDialog {
  submit(formdata) {
    R.smbresourcesAPI.createSMBResource(formdata, this.apiCallback.bind(this));
  }

  onSuccess(data) {
    location.reload();
  }
}

class SMBResourcesView {
  constructor(params) {
    this.params = params;
  }

  onDocumentReady() {
    new NewSMBResourceDialog('#dlg-new-smbresource');

    new ConfirmDeleteDialog({'smbresource': (id) => {
      R.smbresourcesAPI.deleteSMBResource(id, (error, data, response) => {
        if (!R.responseHasError(response)) {
          location.reload();
        }
      });
    }});

    // set up editables
    $('.editable').texteditable();
    $('.editable').setup_triggers();
  }
}

export default SMBResourcesView;
