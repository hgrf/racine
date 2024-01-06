import R from '../racine';

import FormDialog from './formdialog';

class NewUserDialog extends FormDialog {
  submit(formdata) {
    R.usersAPI.createUser(formdata, this.apiCallback.bind(this));
  }

  onSuccess(data) {
    location.reload();
  }
}

export default NewUserDialog;
