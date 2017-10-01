var sample_id;
var showparentactions = false;

// configure the CKEditor
var ckeditorconfig = {
    extraPlugins: 'save',
    imageUploadUrl: '/browser/upload?caller=ckdd&type=img',
    uploadUrl: '/browser/upload?caller=ckdd&type=att',
    filebrowserImageBrowseUrl: '/browser',
    filebrowserImageUploadUrl: '/browser/upload?caller=ckb&type=img',
    filebrowserLinkUploadUrl: '/browser/upload?caller=ckb&type=att',
    filebrowserWindowWidth: 800,
    filebrowserWindowHeight: 500,
	toolbarGroups: [
		{ name: 'clipboard', groups: [ 'clipboard', 'undo' ] },
		{ name: 'editing', groups: [ 'find', 'selection', 'spellchecker', 'editing' ] },
		{ name: 'forms', groups: [ 'forms' ] },
		{ name: 'document', groups: [ 'mode', 'document', 'doctools' ] },
		{ name: 'others', groups: [ 'others' ] },
		{ name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ] },
		{ name: 'styles', groups: [ 'styles' ] },
		{ name: 'paragraph', groups: [ 'list', 'indent', 'blocks', 'align', 'bidi', 'paragraph' ] },
		{ name: 'links', groups: [ 'links' ] },
		{ name: 'insert', groups: [ 'insert' ] },
		{ name: 'colors', groups: [ 'colors' ] },
		{ name: 'about', groups: [ 'about' ] },
		{ name: 'tools', groups: [ 'tools' ] }
	],
    removeButtons: 'Cut,Copy,Paste,PasteText,PasteFromWord,Undo,Redo,BGColor,RemoveFormat,Outdent,Indent,Blockquote,About,Strike,Scayt,Anchor,Source'
};

$.event.props.push('dataTransfer');   // otherwise jQuery event does not have function dataTransfer

function init_editor() {
    sample_id = $('#sampleid').text();

    // handler for matrix view button
    $('#matrixviewbutton').click(function() {
        load_matrix_view(sample_id);
    });

    // handler for archive button
    $('#archive').click(function() {
        $.ajax({
            url: "/togglearchived",
            type: "post",
            data: { "id": sample_id },
            success: function( data ) {
                if(data.isarchived) {
                    $('#archive').attr('title', 'De-archive');
                    $('#archive').attr('src', '/static/dearchive.png');
                    $('#'+$('#sampleid').text()+'.nav-entry').addClass('nav-entry-archived');
                } else {
                    $('#archive').attr('title', 'Archive');
                    $('#archive').attr('src', '/static/archive.png');
                    $('#'+$('#sampleid').text()+'.nav-entry').removeClass('nav-entry-archived');
                }
            }
        });
    });

    $('#showparentactions').click(function() {
        showparentactions = !showparentactions; // toggle
        load_sample($('#sampleid').text());
    });

    // handler for button that changes sample image
    $('#changesampleimage').click(function(event) {
        window.open("/browser?changesampleimage=1&sample="+sample_id, 'Browser', 'height=500, width=800, scrollbars=yes')
    });

    // handler for new action submit button
    $('#submit').click( function(event) {
        for ( instance in CKEDITOR.instances ) CKEDITOR.instances[instance].updateElement(); // otherwise content of editor is not transmitted
        $.ajax({
            url: "/newaction/"+sample_id,
            type: "post",
            data: $('#newactionform').serialize(),
            success: function( data ) {
                if(data.code == 0) {
                    load_sample(sample_id);
                }
                else {      // form failed validation; because of invalid data or expired CSRF token
                    $(document).on("editor_initialised", data, function(event) {
                        CKEDITOR.instances.description.setData(event.data.description);
                        $("#errordialog").find(".modal-body").text("Form is not valid. Either you entered an invalid date or the session has expired. Try submitting again.");
                        $("#errordialog").modal("show");
                        $(document).off("editor_initialised");
                    });
                    load_sample($('#sampleid').text());
                }
            }
        });
        event.preventDefault();
    });

    // put lightbox link around images
    $('#sampledescription').find('img').wrap(function() { return '<a class="lightboxlink" href="'+this.src+'" data-lightbox="'+sample_id+'">'; });
    $('.actiondescription').find('img').wrap(function() { return '<a class="lightboxlink" href="'+this.src+'" data-lightbox="'+sample_id+'">'; });
    $('#sampleimage').wrap(function() { return '<a class="lightboxlink" href="'+this.src+'" data-lightbox="'+$('#sampleid').text()+'">'; });

    // typeset all equations
    if(MathJax.isReady)         // if it is not ready now, it should typeset automatically once it is ready
        MathJax.Hub.Queue(["Typeset",MathJax.Hub]);

    // tell CKEditor browser to pass on sample ID
    ckeditorconfig.filebrowserImageBrowseUrl = '/browser?sample='+sample_id;
    CKEDITOR.replace('description', ckeditorconfig);

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // set up editables (i.e. in-situ editors)

    // add a trigger image to all editables
    $('.editable').setup_triggers();

    // set up editors for sample and action descriptions (CKEditors)
    $('.ckeditable').ckeditable();

    // other editables:
    $('#samplename.editable').texteditable();
    $('#samplename.editable').on('editableupdate', function(event, data) {
        if(!data.code) // only if no error occured
            $("#navname"+sample_id).html(data.value);
    });
    $('.actiondate.editable').texteditable();

    $('.swapaction').click( function(event) {
        sampleid = sample_id;
        actionid = $(this).data('id');
        swapid = $(this).data('swapid');
        $.ajax({
            url: "/swapactionorder",
            type: "post",
            data: { "actionid": actionid,
                    "swapid": swapid },
            success: function( data ) {
                load_sample(sampleid);
            }
        });
    });

    $(document).trigger("editor_initialised");
}

function load_sample(id, pushstate) {
    var pushstate = typeof pushstate !== 'undefined' ?  pushstate : true;

    // if currently viewing a sample (not welcome page) then change the navbar background to transparent before loading
    // the new sample
    if($('#sampleid').text() != "")
        $('#' + sample_id + ".nav-entry").css("background-color", "transparent");

    // load the sample data and re-initialise the editor
    $.ajax({
        url: "/editor/"+id+(showparentactions ? "?showparentactions=1" : ""),
        pushstate: pushstate,
        success: function( data ) {
            $( "#editor-frame" ).html(data);
            sample_id = $('#sampleid').text();
            if(this.pushstate)
                window.history.pushState({"id": sample_id, "pageTitle": data.pageTitle}, "", "/sample/"+ sample_id);
            document.title = "MSM - "+$('#samplename').text();
            init_editor();

            $('#'+sample_id+".nav-entry").css("background-color", "#BBBBFF");
        }
    });
}

$(document).ready(function() {
    window.addEventListener("popstate", function(e) {
        if(e.state != null)
            load_sample(e.state.id, false);
        else
            location.href = "/";
    });

    // load sample if we're not on welcome page
    if(typeof sample == "undefined") {
        $.ajax({
            url: "/welcome",
            success: function(data) {
                $("#editor-frame").html(data);
            }
        });
    } else {
        load_sample(sample);
    }

    // add window unload handler (which asks the user to confirm leaving the page when one of the CKEditor instances
    // has been modified
    window.addEventListener('beforeunload', function(e) {
        for(var i in CKEDITOR.instances) {
            if(CKEDITOR.instances[i].checkDirty()) {
                confirmationMessage = "Are you sure you want to leave before saving modifications?";
                e.returnValue = confirmationMessage;     // Gecko, Trident, Chrome 34+
                return confirmationMessage;              // Gecko, WebKit, Chrome <34
            }
        }
    });

    // TODO: this stuff belongs in "main.js"

    // sample and action deletion
    $('#confirm-delete').on('show.bs.modal', function(e) {
        $(this).find('.btn-ok').attr('id', $(e.relatedTarget).data('id'));
        $(this).find('.btn-ok').data('type', $(e.relatedTarget).data('type'));
        $('.debug-id').html('Delete <strong>'+$(e.relatedTarget).data('type')+'</strong> ID: <strong>' + $(this).find('.btn-ok').attr('id') + '</strong>');
    });

    $('.btn-ok').click( function(event) {
        var type = $(this).data('type');
        var id = $(this).attr('id');
        $.ajax({
            url: "/del"+type+"/"+id,
            success: function( data ) {
                if(type=="sample")
                    location.href = "/";
                if(type=="action")
                    $('#'+id+'.list-entry').remove();
                if(type=="share") {
                    if(data.code==2) // if the user removed himself from the sharer list
                        location.href = "/";
                    $('#sharelistentry'+data.shareid).remove();
                }
                $('#confirm-delete').modal('hide');
            }
        });
    });

    // user browser (for sample sharing)
    $('#userbrowser').on('show.bs.modal', function(e) {
        $.ajax({
            url: "/userlist",
            type: "post",
            data: { "id": $('#sampleid').text() },
            success: function( data ){
                $("#userbrowser-frame").html(data);

                // use .one to avoid multiple clicks and creation of multiple identical shares
                $('.user').one('click', function( event ) {
                    $.ajax({
                        url: "/sharesample",
                        type: "post",
                        data: { "id": sample_id, "sharewith": $(this).attr('id') },
                        success: function( data ) {
                            $('#sharelist').append('<div class="sharelistentry" id="sharelistentry'+data.shareid+'"><a data-type="share" data-id="'+data.shareid+'" data-toggle="modal" data-target="#confirm-delete" href=""><i class="glyphicon glyphicon-remove"></i></a>\n'+data.username+'</div>');
                            $('#userbrowser').modal('hide');
                        }
                    }); // what if we drag parent to child?
                });
            }
        });
    });
});