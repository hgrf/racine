// tell MathJax to align left even if it's not loaded yet
window.MathJax = {
    displayAlign: "left"
};

// configure the CKEditor
var ckeditorconfig = {
    filebrowserImageBrowseUrl : '/browser',
    filebrowserWindowWidth  : 800,
    filebrowserWindowHeight : 500,
    toolbar:
    [
        ['Bold', 'Italic', 'Underline','Subscript','Superscript', 'Format', 'Styles', '-', 'NumberedList', 'BulletedList', 'HorizontalRule', '-', 'Link', 'Unlink', '-', 'Image', 'Table', 'SpecialChar', '-', 'Maximize'],
        ['UIColor']
    ]
};

$.event.props.push('dataTransfer');   // otherwise jQuery event does not have function dataTransfer

function init_editor() {
    // handler for matrix view button
    $('#matrixviewbutton').click(function() {
        load_matrix_view($('#sampleid').text());
    });

    // handler for archive button
    $('#archive').click(function() {
        $.ajax({
            url: "/togglearchived",
            type: "post",
            data: { "id": $('#sampleid').text() },
            success: function( data ) {
                if(data.isarchived) {
                    $('#archive').attr('title', 'De-archive');
                    $('#archive').attr('src', '/static/dearchive.png');
                } else {
                    $('#archive').attr('title', 'Archive');
                    $('#archive').attr('src', '/static/archive.png');
                }
            }
        });
    });

    // handler for button that changes sample image
    $('#changesampleimage').click(function(event) {
        window.open("/browser?sample="+$("#sampleid").text(), 'Browser', 'height=500, width=800, scrollbars=yes')
    });

    // handler for new action submit button
    $('#submit').click( function(event) {
        for ( instance in CKEDITOR.instances ) CKEDITOR.instances[instance].updateElement(); // otherwise content of editor is not transmitted
        $.ajax({
            url: "/newaction/"+$('#sampleid').text(),
            type: "post",
            data: $('#newactionform').serialize(),
            success: function( data ) {
                load_sample($('#sampleid').text());
            }
        });
        event.preventDefault();
    });

    // put lightbox link around images
    $('.actiondescription').find('img').wrap(function() { return '<a class="lightboxlink" href="'+this.src+'" data-lightbox="'+$('#sampleid').text()+'">'; });
    $('#sampleimage').wrap(function() { return '<a class="lightboxlink" href="'+this.src+'" data-lightbox="'+$('#sampleid').text()+'">'; });

    // typeset all equations
    if(MathJax.isReady)
        MathJax.Hub.Queue(["Typeset",MathJax.Hub]);

    // tell CKEditor browser to pass on sample ID
    ckeditorconfig.filebrowserImageBrowseUrl = '/browser?sample='+$("#sampleid").text();
    CKEDITOR.replace( 'description', ckeditorconfig);

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // handlers for fields that modify sample information (jEditables)
    $('.editsamplename').editable('/changesamplename', {
        style: 'inherit',
        event     : "dblclick",
        callback : function(value, settings) {
            var json = $.parseJSON(value);
            $( ".editsamplename" ).html(json.name);
            if(json.code == 0) {
                $("#navname" + json.id).html(json.name);
            } else {
                $( "#flashmessages" ).append(begin_flashmsg+json.error+end_flashmsg);
            }
        }
    });

    $('.selectsampletype').editable('/changesampletype', {
        data   : sampletypes,
        style  : 'inherit',
        type   : 'select',
        submit : 'OK',
        event     : "dblclick",
        callback : function(value, settings) {
            $( "#navtype"+$('#sampleid').text() ).html(value);
        }
    });

    $('.editsampledescription').editable('/changesampledesc', {
        type: 'ckeditor',
        submit: 'OK',
        cancel: 'Cancel',
        onblur: "ignore",
        event     : "dblclick",
        ckeditor: ckeditorconfig
    });

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // handlers for fields that modify action information (jEditables and the order buttons)
    $('.editactiondate').editable('/changeactiondate', {
        style: 'inherit',
        submit: 'OK',
        event     : "dblclick",
        callback : function(value, settings) {
            var json = $.parseJSON(value);
            $( "#"+json.id+".editactiondate" ).html(json.date);
            if(json.code != 0) {
                $( "#flashmessages" ).append(begin_flashmsg+json.error+end_flashmsg);
            }
        }
    });

    $('.selectactiontype').editable('/changeactiontype', {
        data   : actiontypes,
        style  : 'inherit',
        type   : 'select',
        submit : 'OK',
        event     : "dblclick"
    });

    $(".editactiondescription").editable('/changeactiondesc', {
        type   : 'ckeditor',
        submit : 'OK',
        cancel:  'Cancel',
        onblur: "ignore",
        event     : "dblclick",
        loadurl: '/getactiondesc',
        ckeditor : ckeditorconfig,
        callback: function() {
            // typeset all equations in this action
            MathJax.Hub.Queue(["Typeset",MathJax.Hub,$(this).get()]);

            // put back lightbox link around images
            $(this).find('img').wrap(function() { return '<a class="lightboxlink" href="'+this.src+'" data-lightbox="'+$('#sampleid').text()+'">'; });
        }
    });

    $('.swapaction').click( function(event) {
        sampleid = $('#sampleid').text();
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
}

function load_sample(id) {
    // a kind of ugly workaround to read out the current status of the "show parent actions" button
    //hideparentactions = ($('#parentactions').text().split(' ')[0] == 'Show');

    // if currently viewing a sample (not welcome page) then change the navbar background to transparent before loading
    // the new sample
    if($('#sampleid').text() != "")
        $('#'+$('#sampleid').text()+".nav-entry").css("background-color", "transparent");

    // load the sample data and re-initialise the editor
    $.ajax({
        url: "/editor/"+id+(hideparentactions ? "?hideparentactions=1" : ""),
        success: function( data, id ) {
            $( "#editor-frame" ).html(data);
            window.history.pushState({"html": data, "pageTitle": data.pageTitle}, "", "/sample/"+ $('#sampleid').text());
            init_editor();

            $('#'+$('#sampleid').text()+".nav-entry").css("background-color", "#BBBBFF");
        }
    });
}

$(document).ready(function() {
    // load sample if we're not on welcome page
    if(typeof sample != "undefined") {
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

                $('.user').dblclick( function( event ) {
                    $.ajax({
                        url: "/sharesample",
                        type: "post",
                        data: { "id": $('#sampleid').text(), "sharewith": $(this).attr('id') },
                        success: function( data ) {
                            $('#sharelist').append('<div class="row sharelistentry" id="sharelistentry'+data.shareid+'">'+data.username+'<img style="cursor: pointer; float: left; display: inline;" width="32" height="32" src="/static/delete.png" data-type="share" data-id="'+data.shareid+'" data-toggle="modal" data-target="#confirm-delete"></div>');
                            $('#userbrowser').modal('hide');
                        }
                    }); // what if we drag parent to child?
                });
            }
        });
    });
});