import $ from "jquery";

import substringMatcher from "../util/substringmatcher";

function shareselected(event, suggestion) {
  R.sharesAPI.createShare(
      {'sampleid': R.state.sampleid, 'username': $('#username').val()},
      function(error, data, response) {
        if (!response) {
          R.errorDialog('Server error. Please check your connection.');
        } else if (response.error) {
          if (response.body.message) {
            R.errorDialog(response.body.message);
          } else {
            R.errorDialog(response.error);
          }
        } else {
          $('#sharelist').append(
              `<div class="sharelistentry" id="sharelistentry${data.shareid}">
              <a data-type="share" data-id="${data.shareid}" data-toggle="modal"
                  data-target="#confirm-delete" href="">
                <i class="glyphicon glyphicon-remove"></i>
              </a>${data.username}
              </div>`,
          );
        }
        $('#userbrowser').modal('hide');
      },
  );
}

class UserBrowserDialog {
  constructor() {
    // set up the OK button and the enter button
    $('#userbrowserok').click(shareselected);
    $('#username').keyup(function(ev) {
      if (ev.keyCode == 13) shareselected();
    });

    // user browser (for sample sharing)
    $('#userbrowser').on('show.bs.modal', function(event) {
      // empty the text field and disable autocompletion
      $('#username').val('');
      $('#username').typeahead('destroy');

      // empty recent collaborators list
      $('#recent-collaborators').html('');

      // update autocompletion for the text field and recent collaborators list
      $.ajax({
        url: '/userlist',
        type: 'post',
        data: {'mode': 'share', 'sampleid': R.state.sampleid},
        success: function(data) {
          // set up autocompletion
          $('#username').typeahead({
            minLength: 1,
            highlight: true,
          },
          {
            name: 'users',
            source: substringMatcher(data.users),
            templates: {
              suggestion: function(data) {
                return `<div>
                  <img src="/static/images/user.png" width="24px" height="24px">
                  ${data}
                  </div>`;
              },
            },
          });
          // make recent collaborators list
          if (data.recent.length > 0) {
            $('#recent-collaborators').append(
                '<div>Recent collaborators:<br>&nbsp</div>',
            );
          }
          for (const i in data.recent) {
            $('#recent-collaborators').append(
                `<div class="user" data-name="${data.recent[i]}">
                  <img src="/static/images/user.png">${data.recent[i]}
                </div>`,
            );
          }
          // set up click event
          $('.user').one('click', function(event) {
            $('#username').val($(this).data('name'));
            shareselected();
          });
        },
      });
    });

    // once the modal dialog is open, put the cursor in the username field
    $('#userbrowser').on('shown.bs.modal', function(event) {
      $('#username').focus();
    });
  }
}

export default UserBrowserDialog;
