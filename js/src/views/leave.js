import $ from 'jquery';
import R from '../racine';

import substringMatcher from '../util/substringmatcher';

class LeaveView {
  constructor(params) {
    this.params = params;
  }

  onDocumentReady() {
    // set up the OK button and the enter button
    function leave() {
      location.href = '/profile/leave?heir='+$('#username').val();
    }
    $('#userbrowserok').click(leave);
    $('#username').keyup(function(ev) {
      if (ev.keyCode == 13) leave();
    });


    // set up autocompletion for the text field
    R.usersAPI.getUserList({mode: 'leave'}, (error, data, response) => {
      if (!R.responseHasError(response)) {
        $('#username').typeahead({
          minLength: 1,
          highlight: true,
        },
        {
          name: 'users',
          source: substringMatcher(data.users),
          templates: {
            suggestion: (data) => `<div><i class="${R.icons.userAlt}"></i>${data}</div>`,
          },
        });
      }
    });

    $('#confirm').click(function( event ) {
      const heir = $(this).data('heir'); // eslint-disable-line no-invalid-this
      location.href = `/profile/leave?heir=${heir}&confirm=1`;
    });

    $('#reactivate').click(function( event ) {
      location.href = '/profile/leave?reactivate=1';
    });
  }
}

export default LeaveView;
