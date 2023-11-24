import $ from 'jquery';
import R from '../racine';

class EmailView {
  constructor(params) {
    this.task_id = params.task_id;
  }

  onDocumentReady() {
    $('#emailform').submit(function(event) {
      event.preventDefault();
      const formData = new FormData(this); // eslint-disable-line no-invalid-this

      $('#overlaytext').text('Sending mail...');
      $('#overlay').css('display', 'block');

      $.ajax({
        url: '/settings/email',
        data: formData,
        type: 'POST',
        contentType: false,
        processData: false,
        success: function(data) {
          const taskId = data.task_id;

          function callback(error, data, response) {
            if (data.state === 'PENDING' || data.state === 'RUNNING') {
              setTimeout(function() {
                R.defaultAPI.getMailProgress(taskId, callback);
              }, 1000);
            } else if (data.state === 'SUCCESS') {
              $('#overlay').css('display', 'none');
              $('#flashmessages').append(
                  '<div class=\'alert alert-warning col-sm-9 col-md-10\'>' +
                  '<button type=\'button\' class=\'close\' data-dismiss=\'alert\'>' +
                    '&times;' +
                  '</button>' +
                  data.status +
                '</div>',
              );
            } else if (data.state === 'FAILURE') {
              $('#overlay').css('display', 'none');
              $('#flashmessages').append(
                  '<div class=\'alert alert-warning col-sm-9 col-md-10\'>' +
                  '<button type=\'button\' class=\'close\' data-dismiss=\'alert\'>' +
                    '&times;' +
                  '</button>' +
                  data.status +
                '</div>',
              );
            }
          }
          R.defaultAPI.getMailProgress(taskId, callback);
        },
        error: function(jqXHR, textStatus, errorThrown) {
          console.error('Error when communicating with server.');
        },
      });
    });
  }
}

export default EmailView;
