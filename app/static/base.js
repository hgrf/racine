function Dialog(id, title, class_, hasFooter) {
    $('#modal-dialogs').prepend(      // using prepend so that first added dialog (error dialog) has priority in z-order
        '<div class="modal fade" id="'+id+'" tabindex="-1" role="dialog" aria-labelledby="myModalLabel"'+
             'aria-hidden="true">'+
            '<div class="modal-dialog '+class_+'">'+
                '<div class="modal-content">'+
                    '<div class="modal-header">'+
                        '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>'+
                        '<h4 class="modal-title" id="myModalLabel">'+title+'</h4>'+
                    '</div>'+
                    '<div class="modal-body"></div>'+
                    (hasFooter ? '<div class="modal-footer"></div>' : '')+
                '</div>'+
            '</div>'+
        '</div>'
    );

    this.dialog = $('#modal-dialogs').find('#'+id).first();
    this.body = this.dialog.find('div.modal-body').first();
    this.footer = hasFooter ? this.dialog.find('div.modal-footer').first() : undefined;

    // remap bootstrap dialog events
    let this_object = this;
    this.dialog.on('show.bs.modal', function(event) { this_object.onShow(event); });
    this.dialog.on('shown.bs.modal', function(event) { this_object.onShown(event); });
    this.dialog.on('hide.bs.modal', function(event) { this_object.onHide(event); });

    return this;
}

Dialog.prototype.show = function() {
    this.dialog.modal('show');
};

Dialog.prototype.hide = function() {
    this.dialog.modal('hide');
};

Dialog.prototype.onShow = function(event) {};
Dialog.prototype.onShown = function(event) {};
Dialog.prototype.onHide = function(event) {};

function mobile_hide_sidebar() {
    $('#toggle-sidebar').removeClass('active');
    $('.sidebar').removeClass('overlay');
    $('.content-overlay').fadeOut();
}

var errordialog;

$(document).ready(function() {
    // set up error dialog
    errordialog = new Dialog('errordialog', 'Error', '', true);
    errordialog.footer.html('<button type="button" class="btn btn-primary" data-dismiss="modal">OK</button>');
    errordialog.showMessage = function(message) {
        errordialog.body.text(message);
        errordialog.show();
    };

    // set up confirmation dialog for deletion of samples, actions, shares, users and smbresources
    confirmdeletedialog = new Dialog('confirm-delete', 'Confirm delete', '', true);
    confirmdeletedialog.body.html(
        '<p>You are about to delete an item, this procedure is irreversible.</p>'+
        '<p>Do you want to proceed?</p>'+
        '<p class="debug-id"></p>'
    );
    confirmdeletedialog.footer.html(
        '<button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>'+
        '<a class="btn btn-danger btn-ok">Delete</a>'
    );

    $('#toggle-sidebar').click(function () {
        if ($('.sidebar').hasClass('overlay')) {
            $('.sidebar').removeClass('overlay');
            $('.content-overlay').fadeOut();
        } else {
            $('.sidebar').addClass('overlay');
            $('.content-overlay').fadeIn();
        }
    });

    $('.content-overlay').click(function() {
        mobile_hide_sidebar();
    });

    $('.nav-button-toggle').click(function () {
        if ($(this).hasClass('active')) {
            $(this).removeClass('active');
        } else {
            $(this).addClass('active');
        }
    });
});