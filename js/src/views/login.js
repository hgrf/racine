import R from '../racine';
import $ from 'jquery';

import substringMatcher from '../util/substringmatcher';

class LoginView {
  constructor(params) {
    this.params = params;
  }

  onDocumentReady() {
    const self = this;

    $('.user').click(function( event ) {
      const username = $(this).data('username'); // eslint-disable-line no-invalid-this
      $('#username').val(username);
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
          return `<div><i class="${R.icons.userAlt}"></i>${data}</div>`;
        },
      },
    });
  }
}

export default LoginView;
