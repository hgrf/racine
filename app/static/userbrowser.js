function UserBrowserDialog(id, sharelist) {
    Dialog.call(this, id, 'Select a user', '', true);
    this.body.html(
        '<div>Select a user you want to share this sample with:<br>&nbsp;</div>' +
        '<div class="form-group input-group">' +
        '<span class="input-group-addon"><i class="glyphicon glyphicon-user"></i></span>' +
        '<input type="text" id="username" class="form-control" placeholder="username">' +
        '</div>' +
        '<div id="recent-collaborators"></div>'
    );

    this.footer.html(
        '<button id="userbrowserok" type="button" class="btn btn-primary" data-dismiss="modal">OK</button>' +
        '<button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>'
    );

    this.sharelist = sharelist;

    // store DOM elements in variables
    this.username = this.body.find('#username');
    this.recentcollaborators = this.body.find('#recent-collaborators');
    this.userbrowseropk = this.footer.find('#userbrowserok');

    // set up the OK button and the enter button
    let this_obj = this;
    this.userbrowseropk.click(this_obj.shareselected);
    this.username.keyup(function(ev) { if(ev.keyCode == 13) this_obj.shareselected(); });

    return this;
}

UserBrowserDialog.prototype = Object.create(Dialog.prototype);

UserBrowserDialog.prototype.onShow =function() {
    // empty the text field and disable autocompletion
    this.username.val('');
    this.username.typeahead('destroy');

    // empty recent collaborators list
    this.recentcollaborators.html('');

    let this_obj = this;

    // update autocompletion for the text field and recent collaborators list
    $.ajax({
        url: "/userlist",
        type: "post",
        data: {"mode": "share", "sampleid": sample_id},
        success: function(data) {
            // set up autocompletion
            this_obj.username.typeahead({
                minLength: 1,
                highlight: true
            },
            {
                name: 'users',
                source: substringMatcher(data.users),
                templates: {
                    suggestion: function(data) {
                        return '<div><img src="/static/images/user.png" width="24px" height="24px">'+data+'</div>';
                    }
                }
            });
            // make recent collaborators list
            if(data.recent.length > 0)
                this_obj.recentcollaborators.append('<div>Recent collaborators:<br>&nbsp</div>');
            for(i in data.recent)
                this_obj.recentcollaborators.append(
                    '<div class="user" data-name="'+data.recent[i]+'">'+
                        '<img src="/static/images/user.png">'+
                        data.recent[i]+
                    '</div>'
                );
            // set up click event
            this_obj.recentcollaborators.find('.user').one('click', function() {
               $('#username').val($(this).data('name'));
               this_obj.shareselected();
            });
        }
    });
};

UserBrowserDialog.prototype.onShown = function() {
    // once the modal dialog is open, put the cursor in the username field
    $('#username').focus();
};

UserBrowserDialog.prototype.shareselected = function(event, suggestion) {
    let this_obj = this;
    $.ajax({
        url: "/createshare",
        type: "post",
        data: { "sampleid": sample_id, "username": $('#username').val() },
        success: function( data ) {
            this_obj.hide();
            this_obj.sharelist.append(
                '<div class="sharelistentry" id="sharelistentry'+data.shareid+'">'+
                    '<a data-type="share" data-id="'+data.shareid+'" data-toggle="modal"' +
                       'data-target="#confirm-delete" href="">' +
                        '<i class="glyphicon glyphicon-remove"></i>' +
                    '</a>'+
                    data.username+
                '</div>');
        },
        error: function( request, status, message ) {
            this_obj.hide();
            errordialog.showMessage(request.responseJSON.error);
        }
    });
};