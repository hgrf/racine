import $ from 'jquery';

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
    $.ajax({
      url: '/userlist',
      type: 'post',
      data: {'mode': 'leave'},
      success: function( data ) {
        $('#username').typeahead({
          minLength: 1,
          highlight: true,
        },
        {
          name: 'users',
          source: substringMatcher(data.users),
          templates: {
            suggestion: function(data) {
              return '<div><img src="/static/images/user.png" width="24px" height="24px">' +
                data + '</div>';
            },
          },
        });
      },
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
