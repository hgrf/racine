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
    this.newsamplename = $('#newsamplename');
    this.newsampleparent = $('#newsampleparent');
    this.newsampleparentid = $('#newsampleparentid');

    createSelectSample(this.newsampleparent, this.newsampleparentid);
    CKEDITOR.replace('newsampledescription', ckeditorconfig);

    this.clearButton.on('click', function(event) {
      event.preventDefault();

      self.newsamplename.val('');
      self.newsampleparent.typeahead('val', '');
      self.newsampleparent.markvalid();
      self.newsampleparentid.val('');
      CKEDITOR.instances['newsampledescription'].setData('');
    });
  }

  onShow() {
    // set the parent field to the current sample
    if ('sampleid' in this.mainView.state) {
      this.newsampleparent.typeahead('val', $('#samplename').text());
      this.newsampleparentid.val(this.mainView.state.sampleid);
    }
  }

  onShown() {
    /* Workaround for a bug in CKEditor:
     * If we don't do this after the editor is shown, a <br /> tag is inserted if we tab to the
     * editor.
     */
    CKEDITOR.instances['newsampledescription'].setData('');

    // put the cursor in the sample name field
    this.newsamplename.focus();
  }

  onHide() {
    // clear the dialog
    this.clearButton.trigger('click');
  }

  submit(formdata) {
    // make sure content of editor is transmitted
    CKEDITOR.instances['newsampledescription'].updateElement();

    R.samplesAPI.createSample(formdata, this.makeAPICallback());
  }

  onSuccess(data) {
    this.mainView.loadSample(data.sampleid);
    this.mainView.tree.load(true);
  }
}

export default NewSampleDialog;
