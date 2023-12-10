import $ from 'jquery';
import R from '../racine';

import TimedLoader from '../util/timedloader';

class EmailView {
  constructor(params) {
    this.task_id = params.task_id;
    this.spinner = new TimedLoader(10000, false);
  }

  onDocumentReady() {
    const self = this;

    $('#emailform').submit(function(event) {
      event.preventDefault();
      const formData = new FormData(this); // eslint-disable-line no-invalid-this

      $('#overlaytext').html(
          'Sending test email...<br/>' +
          '<canvas id="timed-loader" width="300" height="300"></canvas>',
      );
      self.spinner.start();
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
