import $ from 'jquery';

class FormDialog {
  constructor(dialog, form, submitButton) {
    const self = this;

    this.dialog = $(dialog);
    this.form = $(form);
    this.submitButton = $(submitButton);

    this.submitButton.on('click', function(event) {
      event.preventDefault();

      // clean up error messages
      self.form.find('.form-group').removeClass('has-error');
      self.form.find('span.help-block').remove();

      const formdata = {};
      self.form.serializeArray().map(function(x) {
        formdata[x.name] = x.value;
      });

      self.submit(formdata);
    });
  }

  submit(formdata) {
  }

  onSuccess() {
  }

  makeAPICallback() {
    const self = this;

    return function(error, data, response) {
      if (!response) {
        R.errorDialog('Server error. Please check your connection.');
      } else if (response.body && response.body.error) {
        // form failed validation; because of invalid data or expired CSRF token
        for (const field in response.body.error) {
          if (!Object.hasOwn(response.body.error, field)) {
            continue;
          }
          if (field === 'csrf_token') {
            R.errorDialog('The CSRF token has expired. Please reload the page.');
            continue;
          }
          // get form group
          const formgroup = $(`#${field}`).closest('.form-group');
          // add the has-error to the form group
          formgroup.addClass('has-error');
          // add the error message to the form group
          for (const i in response.body.error[field]) {
            if (Object.hasOwn(response.body.error, field)) {
              formgroup.append(`<span class="help-block">${response.body.error[field][i]}</span>`);
            }
          }
        }
      } else {
        self.dialog.modal('hide');
        self.onSuccess();
      }
    };
  }
}

export default FormDialog;
