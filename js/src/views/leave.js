import $ from 'jquery';

import substringMatcher from '../util/substringmatcher';

class LeaveView {
  constructor() {
    this.state = {};
  }

  load(state) {
    this.state = state;
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
        // TODO
        $('#username').typeahead({
          minLength: 1,
          highlight: true,
        },
        {
          name: 'users',
          source: substringMatcher(data.users),
          templates: {
            suggestion: function(data) {
              return '<div><img src="/static/images/user.png" width="24px" height="24px">' + data + '</div>';
            },
          },
        });
      },
    });

    $('#confirm').click(function( event ) {
      location.href = '/profile/leave?heir='+$(this).data('heir')+'&confirm=1';
    });

    $('#reactivate').click(function( event ) {
      location.href = '/profile/leave?reactivate=1';
    });
  }
}

export default LeaveView;
