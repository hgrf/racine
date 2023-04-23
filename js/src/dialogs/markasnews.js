import $ from 'jquery';

import FormDialog from './formdialog';

class MarkAsNewsDialog extends FormDialog {
  constructor() {
    super('#dlg-mark-as-news');
  }

  show(actionid) {
    // set the action ID hidden field
    this.fields.actionid.val(actionid);
    this.clear();
    this.dialog.modal('show');
  }

  submit(formdata) {
    const actionid = this.fields.actionid.val();
    this.flag = $(`#togglenews-${actionid}`);
    R.actionsAPI.markAsNews(formdata, this.makeAPICallback());
  }

  clear() {
    this.fields.title.val('');
    this.fields.expires.val('');
  }

  onSuccess(data) {
    // toggle the flag
    this.flag.removeClass('markasnews');
    this.flag.addClass('unmarkasnews');
  }
}

export default MarkAsNewsDialog;
