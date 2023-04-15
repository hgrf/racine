import $ from 'jquery';

class MarkAsNewsDialog {
    constructor() {
        $('#dlg_markasnews_submit').click(function (event) {
            event.preventDefault();

            var dlg_markasnews_form = $('#dlg_markasnews_form');
            var actionid = $("#actionid").val();
            var flag_element = $('#togglenews-' + actionid);

            // clean up error messages
            dlg_markasnews_form.find('.form-group').removeClass('has-error');
            dlg_markasnews_form.find('span.help-block').remove();

            var formdata = {};
            dlg_markasnews_form.serializeArray().map(function (x) { formdata[x.name] = x.value; });

            R.actionsAPI.markActionAsNews(formdata, function (error, data, response) {
                if (!response)
                    R.errorDialog("Server error. Please check your connection.");
                else if (response.body && response.body.error) {
                    // form failed validation; because of invalid data or expired CSRF token
                    for (var field in response.body.error) {
                        if (field === 'csrf_token') {
                            R.errorDialog('The CSRF token has expired. Please reload the page.');
                            continue;
                        }
                        // get form group
                        var formgroup = $('#' + field).closest('.form-group');
                        // add the has-error to the form group
                        formgroup.addClass('has-error')
                        // add the error message to the form group
                        for (var i in response.body.error[field]) {
                            formgroup.append(
                                '<span class="help-block">' +
                                response.body.error[field][i] +
                                '</span>'
                            );
                        }
                    }
                } else {
                    // hide the dialog
                    $('#dlg_markasnews').modal('hide');

                    // toggle the flag
                    flag_element.removeClass('markasnews');
                    flag_element.addClass('unmarkasnews');
                }
            });
        });
    }
}

export default MarkAsNewsDialog;