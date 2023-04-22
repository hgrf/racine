import $ from 'jquery';

import {createSelectSample} from '../util/searchsample';
import ckeditorconfig from '../util/ckeditorconfig';

class NewSampleDialog {
  constructor(mainView, selector) {
    const dialog = $(selector);
    const newsampleparent = $('#newsampleparent');
    const newsampleparentid = $('#newsampleparentid');
    createSelectSample(newsampleparent, newsampleparentid);
    CKEDITOR.replace('newsampledescription', ckeditorconfig);

    dialog.on('show.bs.modal', function(event) {
      // set the parent field to the current sample
      if ('sampleid' in mainView.state) {
        $('#newsampleparent').typeahead('val', $('#samplename').text());
        $('#newsampleparentid').val(mainView.state.sampleid);
      }
    });

    dialog.on('shown.bs.modal', function() {
      /* Workaround for a bug in CKEditor:
       * If we don't do this after the editor is shown, a <br /> tag is inserted if we tab to the
       * editor.
       */
      CKEDITOR.instances['newsampledescription'].setData('');

      // put the cursor in the sample name field
      $('#newsamplename').focus();
    });

    dialog.on('hide.bs.modal', function() {
      // clear the dialog
      $('#newsampleclear').trigger('click');
    });

    $('#newsampleclear').click(function(event) {
      event.preventDefault();

      $('#newsamplename').val('');
      newsampleparent.typeahead('val', '');
      newsampleparent.markvalid();
      newsampleparentid.val('');
      CKEDITOR.instances['newsampledescription'].setData('');
    });
    $('#newsamplesubmit').click(function(event) {
      event.preventDefault();

      const newsampleform = $('#newsampleform');

      // clean up error messages
      newsampleform.find('.form-group').removeClass('has-error');
      newsampleform.find('span.help-block').remove();

      // make sure content of editor is transmitted
      CKEDITOR.instances['newsampledescription'].updateElement();

      const formdata = {};
      newsampleform.serializeArray().map(function(x) {
        formdata[x.name] = x.value;
      });

      R.samplesAPI.createSample(formdata, function(error, data, response) {
        if (!response) {
          R.errorDialog('Server error. Please check your connection.');
        } else if (response.error) {
          if (response.body.error) {
            // form failed validation; because of invalid data or expired CSRF token
            for (const field in response.body.error) {
              if (!Object.hasOwn(response.body.error, field)) {
                continue;
              }
              if (field === 'csrf_token') {
                R.errorDialog('The CSRF token has expired. ' +
                  'Please reload the page to create a new sample.');
                continue;
              }
              // get form group
              const formgroupid = (field !== 'newsampleparentid' ? field : 'newsampleparent');
              const formgroup = $('#' + formgroupid).closest('.form-group');
              // add the has-error to the form group
              formgroup.addClass('has-error');
              // add the error message to the form group
              for (const i in response.body.error[field]) {
                if (!Object.hasOwn(response.body.error, field)) {
                  continue;
                }
                formgroup.append(
                    '<span class="help-block">' +
                                    response.body.error[field][i] +
                                    '</span>',
                );
              }
            }
          } else {
            R.errorDialog(response.error);
          }
        } else {
          dialog.modal('hide'); // hide and clear the dialog
          mainView.loadSample(data.sampleid);
          mainView.tree.load(true);
        }
      });
    });
  }
}

export default NewSampleDialog;
