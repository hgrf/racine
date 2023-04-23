import $ from 'jquery';

import FormDialog from './formdialog';

class MarkAsNewsDialog extends FormDialog {
  constructor() {
    super('#dlg-mark-as-news');
  }

  show(actionid) {
    // set the action ID hidden field
    this.fields.actionid.val(actionid);
    // clear other fields
    this.fields.title.val('');
    this.fields.expires.val('');
    this.dialog.modal('show');
  }

  submit(formdata) {
    const actionid = this.fields.actionid.val();
    this.flag = $(`#togglenews-${actionid}`);
    R.actionsAPI.markAsNews(formdata, this.makeAPICallback());
  }

  onSuccess(data) {
    // toggle the flag
    this.flag.removeClass('markasnews');
    this.flag.addClass('unmarkasnews');
  }
}

export default MarkAsNewsDialog;
