import $ from 'jquery';

import FormDialog from './formdialog';

class MarkAsNewsDialog extends FormDialog {
  constructor() {
    super('#dlg-mark-as-news', 'mark-as-news-');
  }

  show(actionid) {
    // set the action ID hidden field
    $(`#${this.prefix}actionid`).val(actionid);
    // clear other fields
    $(`#${this.prefix}title`).val('');
    $(`#${this.prefix}expires`).val('');
    this.dialog.modal('show');
  }

  submit(formdata) {
    const actionid = $(`#${this.prefix}actionid`).val();
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
