import $ from 'jquery';

import substringMatcher from '../util/substringmatcher';

class LoginView {
  constructor(params) {
    this.params = params;
  }

  onDocumentReady() {
    var self = this;

    $('.user').click(function( event ) {
      $('#username').val($(this).data('username'));
      $('#password').focus();
      event.preventDefault();
    });

    $('#username').typeahead({
      minLength: 1,
      highlight: true,
    },
    {
      name: 'users',
      source: substringMatcher(self.params.users),
      templates: {
        suggestion: function(data) {
          return '<div><img src="/static/images/user.png" width="24px" height="24px">' +
            data + '</div>';
        },
      },
    });
  }
}

export default LoginView;
