import $ from 'jquery';

import R from '../racine';
import Dialog from './dialog';

function removePrefix(str, prefix) {
  return str.startsWith(prefix) ? str.slice(prefix.length) : str;
}

class FormDialog extends Dialog {
  constructor(selector) {
    super(selector);

    const self = this;

    this.prefix = this.dialog.find('.modal-dialog').first().data('prefix');
    this.form = this.dialog.find('form').first();
    // prevent default form submission on enter, use this class instead
    this.form.on('keydown', (event) => {
      if (event.keyCode == 13) {
        event.preventDefault();
        self.submitButton.trigger('click');
      } else if (event.keyCode == 27) {
        event.preventDefault();
        self.hide();
      }
    });

    this.fields = Object.fromEntries(
        this.form.find('input').toArray().map(
            (field) => [removePrefix(field.id, this.prefix), $(field)],
        ),
    );

    this.submitButton = this.dialog.find('button.frm-dlg-submit').first();
    this.clearButton = this.dialog.find('button.frm-dlg-clear').first();

    this.submitButton.on('click', function(event) {
      event.preventDefault();

      // clean up error messages
      self.form.find('.form-control').removeClass('is-invalid');
      self.form.find('div.invalid-feedback').remove();

      self.beforeSubmit();

      const formdata = {};
      self.form.serializeArray().map(function(x) {
        formdata[removePrefix(x.name, self.prefix)] = x.value;
      });

      self.submit(formdata);
    });

    this.clearButton.on('click', function(event) {
      event.preventDefault();
      self.clear();
    });
  }

  onHide() {
    this.clear();
  }

  beforeSubmit() {
  }

  submit(formdata) {
  }

  clear() {
    this.form[0].reset();
  }

  onSuccess(data) {
  }

  apiCallback(error, data, response) {
    if (!response) {
      this.dialog.modal('hide');
      R.errorDialog('Server error. Please check your connection.');
    } else if (response.error && !(response.body && response.body.error)) {
      this.dialog.modal('hide');
      R.errorDialog(response.error);
    } else if (response.body && response.body.error) {
      // form failed validation; because of invalid data or expired CSRF token
      for (const field in response.body.error) {
        if (!Object.hasOwn(response.body.error, field)) {
          continue;
        }
        if (field === 'csrf_token') {
          this.dialog.modal('hide');
          R.errorDialog('The CSRF token has expired. Please reload the page.');
          continue;
        }
        // get form group
        const formgroup = $(`#${this.prefix}${field}`).closest('.form-group');
        // add the has-error to the form control
        $(`#${this.prefix}${field}`).addClass('is-invalid');
        // add the error message to the form group
        for (const i in response.body.error[field]) {
          if (Object.hasOwn(response.body.error, field)) {
            formgroup.append(
                `<div class="invalid-feedback">${response.body.error[field][i]}</div>`,
            );
          }
        }
      }
    } else {
      this.dialog.modal('hide');
      this.onSuccess(data);
    }
  }
}

export default FormDialog;
