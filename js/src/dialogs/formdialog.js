import $ from 'jquery';

function removePrefix(str, prefix) {
  return str.startsWith(prefix) ? str.slice(prefix.length) : str;
}

class FormDialog {
  constructor(dialog) {
    const self = this;

    this.dialog = $(dialog);
    this.prefix = this.dialog.find('.modal-body').first().data('prefix');
    this.form = this.dialog.find('form').first();

    this.fields = Object.fromEntries(
      this.form.find('input').toArray().map(
        (field) => [removePrefix(field.id, this.prefix), $(field)]
      )
    );

    this.submitButton = this.dialog.find('button.frm-dlg-submit').first();

    this.dialog.on('show.bs.modal', function(event) {
      self.onShow();
    });

    this.dialog.on('shown.bs.modal', function(event) {
      self.onShown();
    });

    this.dialog.on('hide.bs.modal', function(event) {
      self.onHide();
    });

    this.submitButton.on('click', function(event) {
      event.preventDefault();

      // clean up error messages
      self.form.find('.form-group').removeClass('has-error');
      self.form.find('span.help-block').remove();

      const formdata = {};
      self.form.serializeArray().map(function(x) {
        formdata[removePrefix(x.name, self.prefix)] = x.value;
      });

      self.submit(formdata);
    });
  }

  submit(formdata) {
  }

  onShow() {
  }

  onShown() {
  }

  onHide() {
  }

  onSuccess(data) {
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
          const formgroup = $(`#${self.prefix}${field}`).closest('.form-group');
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
        self.onSuccess(data);
      }
    };
  }
}

export default FormDialog;
