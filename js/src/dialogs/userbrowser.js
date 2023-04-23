import $ from 'jquery';
import Dialog from './dialog';
import substringMatcher from '../util/substringmatcher';

class UserBrowserDialog extends Dialog {
  constructor(sampleid) {
    super('#userbrowser');

    this.sampleid = sampleid;
    this.btnOk = this.dialog.find('#userbrowserok');
    this.searchField = this.dialog.find('#username');
    this.recentCollaborators = $('#recent-collaborators');

    this.btnOk.on('click', () => this.#shareSelected());
    this.searchField.on('keyup', (event) => {
      if (event.keyCode == 13) {
        this.#shareSelected();
      }
    });
  }

  userlistCallback(data) {
    // set up autocompletion
    this.searchField.typeahead(
        {minLength: 1, highlight: true},
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
        },
    );

    // make recent collaborators list
    if (data.recent.length > 0) {
      this.recentCollaborators.append(
          '<div>Recent collaborators:<br>&nbsp</div>',
      );
    }
    for (const i in data.recent) {
      if (Object.hasOwn(data.recent, i)) {
        this.recentCollaborators.append(
            `<div class="user" data-name="${data.recent[i]}">
              <img src="/static/images/user.png">${data.recent[i]}
            </div>`,
        );
      }
    }

    // set up click event
    this.recentCollaborators.find('.user').one(
        'click', (event) => this.#shareWith($(event.target).data('name')),
    );
  }

  onShow(event) {
    // empty the text field and disable autocompletion
    this.searchField.val('');
    this.searchField.typeahead('destroy');

    // empty recent collaborators list
    $('#recent-collaborators').html('');

    // update autocompletion for the text field and recent collaborators list
    $.ajax({
      url: '/userlist',
      type: 'post',
      data: {'mode': 'share', 'sampleid': this.sampleid},
      success: (data) => this.userlistCallback(data),
    });
  }

  onShown(event) {
    this.searchField.trigger('focus');
  }

  #shareWith(username) {
    this.searchField.val(username);
    this.#shareSelected();
  }

  #shareSelected() {
    const self = this;
    R.sharesAPI.createShare(
        {'sampleid': this.sampleid, 'username': this.searchField.val()},
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
                    data-target="#dlg-confirm-delete" href="">
                  <i class="glyphicon glyphicon-remove"></i>
                </a>${data.username}
                </div>`,
            );
          }
          self.dialog.modal('hide');
        },
    );
  }
}

export default UserBrowserDialog;
