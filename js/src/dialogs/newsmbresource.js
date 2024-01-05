import R from '../racine';

import FormDialog from './formdialog';

class NewSMBResourceDialog extends FormDialog {
  submit(formdata) {
    R.smbresourcesAPI.createSMBResource(formdata, this.apiCallback.bind(this));
  }

  onSuccess(data) {
    location.reload();
  }
}

export default NewSMBResourceDialog;
