import $ from 'jquery';

import FormDialog from './formdialog';

import {createSelectSample} from '../util/searchsample';
import ckeditorconfig from '../util/ckeditorconfig';

class NewSampleDialog extends FormDialog {
  constructor(mainView, selector) {
    super(selector);
    this.mainView = mainView;

    createSelectSample(this.fields.parent, this.fields.parentid);
    CKEDITOR.replace(`${this.prefix}description`, ckeditorconfig);
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
    this.clear();
  }

  submit(formdata) {
    // make sure content of editor is transmitted
    CKEDITOR.instances[`${this.prefix}description`].updateElement();

    R.samplesAPI.createSample(formdata, this.apiCallback.bind(this));
  }

  clear() {
    this.fields.name.val('');
    this.fields.parent.typeahead('val', '');
    this.fields.parent.markvalid();
    this.fields.parentid.val('');
    CKEDITOR.instances[`${this.prefix}description`].setData('');
  }

  onSuccess(data) {
    this.mainView.loadSample(data.sampleid);
    this.mainView.tree.load(true);
  }
}

export default NewSampleDialog;
