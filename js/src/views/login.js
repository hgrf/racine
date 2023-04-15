import $ from "jquery";

import substringMatcher from "../util/substringmatcher";

class LoginView {
    constructor() {
        this.state = {};
    }

    load(state) {
        this.state = state;
    }

    onDocumentReady() {
        $(".user").click(function( event )  {
            $("#username").val($(this).data("username"));
            $("#password").focus();
            event.preventDefault();
        });

        $('#username').typeahead({
            minLength: 1,
            highlight: true
        },
        {
            name: 'users',
            source: substringMatcher(this.state.users),
            templates: {
                suggestion: function(data) {
                    return '<div><img src="/static/images/user.png" width="24px" height="24px">' + data + '</div>';
                }
            }
        });
    }
}

export default LoginView;
