import $ from 'jquery';

import FormDialog from './formdialog';

import {createSelectSample} from '../util/searchsample';
import ckeditorconfig from '../util/ckeditorconfig';

class NewSampleDialog extends FormDialog {
  constructor(mainView, selector) {
    super(selector, 'new-sample-');

    const self = this;

    this.mainView = mainView;
    this.clearButton = this.dialog.find('button.frm-dlg-clear').first();
    this.name = $(`#${this.prefix}name`);
    this.parent = $(`#${this.prefix}parent`);
    this.parentid = $(`#${this.prefix}parentid`);

    createSelectSample(this.parent, this.parentid);
    CKEDITOR.replace(`${this.prefix}description`, ckeditorconfig);

    this.clearButton.on('click', function(event) {
      event.preventDefault();

      self.name.val('');
      self.parent.typeahead('val', '');
      self.parent.markvalid();
      self.parentid.val('');
      CKEDITOR.instances[`${self.prefix}description`].setData('');
    });
  }

  onShow() {
    // set the parent field to the current sample
    if ('sampleid' in this.mainView.state) {
      this.parent.typeahead('val', $('#samplename').text());
      this.parentid.val(this.mainView.state.sampleid);
    }
  }

  onShown() {
    /* Workaround for a bug in CKEditor:
     * If we don't do this after the editor is shown, a <br /> tag is inserted if we tab to the
     * editor.
     */
    CKEDITOR.instances[`${this.prefix}description`].setData('');

    // put the cursor in the sample name field
    this.name.focus();
  }

  onHide() {
    // clear the dialog
    this.clearButton.trigger('click');
  }

  submit(formdata) {
    // make sure content of editor is transmitted
    CKEDITOR.instances[`${this.prefix}description`].updateElement();

    R.samplesAPI.createSample(formdata, this.makeAPICallback());
  }

  onSuccess(data) {
    this.mainView.loadSample(data.sampleid);
    this.mainView.tree.load(true);
  }
}

export default NewSampleDialog;
