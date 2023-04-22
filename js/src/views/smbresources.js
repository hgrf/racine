import $ from 'jquery';
import ConfirmDeleteDialog from '../dialogs/confirmdelete';

class SMBResourcesView {
  constructor(params) {
    this.params = params;
  }

  onDocumentReady() {
    new ConfirmDeleteDialog(function(type, id) {
      location.href = `/settings/smbresources?delete=${id}`;
    });

    // set up editables
    $('.editable').texteditable();
    $('.editable').setup_triggers();
  }
}

export default SMBResourcesView;
