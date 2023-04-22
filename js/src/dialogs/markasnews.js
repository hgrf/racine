import $ from 'jquery';

class MarkAsNewsDialog {
  constructor() {
    $('#dlg_markasnews_submit').click(function(event) {
      event.preventDefault();

      const form = $('#dlg_markasnews_form');
      const actionid = $('#actionid').val();
      const flag = $('#togglenews-' + actionid);

      // clean up error messages
      form.find('.form-group').removeClass('has-error');
      form.find('span.help-block').remove();

      const formdata = {};
      form.serializeArray().map(function(x) {
        formdata[x.name] = x.value;
      });

      R.actionsAPI.markActionAsNews(formdata, function(error, data, response) {
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
            const formgroup = $('#' + field).closest('.form-group');
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
          // hide the dialog
          $('#dlg_markasnews').modal('hide');

          // toggle the flag
          flag.removeClass('markasnews');
          flag.addClass('unmarkasnews');
        }
      });
    });
  }
}

export default MarkAsNewsDialog;
