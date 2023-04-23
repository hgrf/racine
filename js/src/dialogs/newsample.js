import $ from 'jquery';

import FormDialog from './formdialog';

import {createSelectSample} from '../util/searchsample';
import ckeditorconfig from '../util/ckeditorconfig';

class NewSampleDialog extends FormDialog {
  constructor(mainView, selector) {
    super(selector);

    const self = this;

    this.mainView = mainView;
    this.clearButton = this.dialog.find('button.frm-dlg-clear').first();

    createSelectSample(this.fields.parent, this.fields.parentid);
    CKEDITOR.replace(`${this.prefix}description`, ckeditorconfig);

    this.clearButton.on('click', function(event) {
      event.preventDefault();

      self.fields.name.val('');
      self.fields.parent.typeahead('val', '');
      self.fields.parent.markvalid();
      self.fields.parentid.val('');
      CKEDITOR.instances[`${self.prefix}description`].setData('');
    });
  }

  onShow() {
    // set the parent field to the current sample
    if ('sampleid' in this.mainView.state) {
      this.fields.parent.typeahead('val', $('#samplename').text());
      this.fields.parentid.val(this.mainView.state.sampleid);
    }
  }

  onShown() {
    /* Workaround for a bug in CKEditor:
     * If we don't do this after the editor is shown, a <br /> tag is inserted if we tab to the
     * editor.
     */
    CKEDITOR.instances[`${this.prefix}description`].setData('');

    // put the cursor in the sample name field
    this.fields.name.focus();
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
