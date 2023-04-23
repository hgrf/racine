import $ from 'jquery';

import FormDialog from './formdialog';

class MarkAsNewsDialog extends FormDialog {
  constructor() {
    super('#dlg_markasnews');
  }

  submit(formdata) {
    const actionid = $('#actionid').val();
    this.flag = $(`#togglenews-${actionid}`);
    R.actionsAPI.markActionAsNews(formdata, this.makeAPICallback());
  }

  onSuccess(data) {
    // toggle the flag
    this.flag.removeClass('markasnews');
    this.flag.addClass('unmarkasnews');
  }
}

export default MarkAsNewsDialog;
