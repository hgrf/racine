import $ from 'jquery';

import FormDialog from './formdialog';

class MarkAsNewsDialog extends FormDialog {
  constructor() {
    super('#dlg-mark-as-news');
  }

  submit(formdata) {
    const actionid = $('#actionid').val();
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
