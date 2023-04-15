import $ from "jquery";

class SMBResourcesView {
    constructor() {
        this.state = {};
    }

    load(state) {
        this.state = state;
    }

    onDocumentReady() {
        $('#confirm-delete').on('show.bs.modal', function (e) {
            $(this).find('.btn-ok').attr('id', $(e.relatedTarget).data('id'));
            $('.debug-id').html('Delete ID: <strong>' + $(this).find('.btn-ok').attr('id') + '</strong>');
        });

        $('.btn-ok').click(function (event) {
            var id = $(this).attr('id');
            location.href = "/settings/smbresources?delete=" + id;
        });

        // set up editables
        $('.editable').texteditable();
        $('.editable').setup_triggers();
    }
}

export default SMBResourcesView;
