import $ from 'jquery';

import substringMatcher from '../util/substringmatcher';

class UserBrowserDialog {
  constructor(mainView) {
    this.mainView = mainView;

    const self = this;

    // set up the OK button and the enter button
    $('#userbrowserok').click(function(event) {
      self.#shareSelected();
    });
    $('#username').keyup(function(ev) {
      if (ev.keyCode == 13) self.#shareSelected();
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
        data: {'mode': 'share', 'sampleid': self.mainView.state.sampleid},
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
            if (Object.hasOwn(data.recent, i)) {
              $('#recent-collaborators').append(
                  `<div class="user" data-name="${data.recent[i]}">
                    <img src="/static/images/user.png">${data.recent[i]}
                  </div>`,
              );
            }
          }
          // set up click event
          $('.user').one('click', function(event) {
            const username = $(this).data('name'); // eslint-disable-line no-invalid-this
            $('#username').val(username);
            self.#shareSelected();
          });
        },
      });
    });

    // once the modal dialog is open, put the cursor in the username field
    $('#userbrowser').on('shown.bs.modal', function(event) {
      $('#username').focus();
    });
  }

  #shareSelected(event, suggestion) {
    R.sharesAPI.createShare(
        {'sampleid': this.mainView.state.sampleid, 'username': $('#username').val()},
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
}

export default UserBrowserDialog;
