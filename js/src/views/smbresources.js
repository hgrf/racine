import $ from 'jquery';
import R from '../racine';
import NewSMBResourceDialog from '../dialogs/newsmbresource';
import ConfirmDeleteDialog from '../dialogs/confirmdelete';

class SMBResourcesView {
  constructor(params) {
    this.params = params;
  }

  onDocumentReady() {
    new NewSMBResourceDialog('#dlg-new-smbresource');

    new ConfirmDeleteDialog({'smbresource': (id) => {
      R.smbresourcesAPI.deleteSMBResource(id, (error, data, response) => {
        location.reload();
        // TODO: handle errors
        // if (!self.#responseHasError(response)) {
        // }
      });
    }});

    // set up editables
    $('.editable').texteditable();
    $('.editable').setup_triggers();
  }
}

export default SMBResourcesView;
