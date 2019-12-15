function NewSampleDialog(id, csrf_token) {
    Dialog.call(this, id, 'New sample', 'modal-lg', true);
    this.body.html(
        '<form id="newsampleform">'+
            '<input id="newsampleparentid" name="newsampleparentid" type="hidden" value="">'+
            '<input id="csrf_token" name="csrf_token" type="hidden" value="'+csrf_token+'">'+
            '<div class="form-group ">'+
                '<label class="control-label" for="newsamplename">Sample name:</label>'+
                '<input class="form-control" id="newsamplename" name="newsamplename" type="text" value="">'+
            '</div>'+
            '<div class="form-group ">'+
                '<label class="control-label" for="newsampleparent">Parent:</label>'+
                '<input class="form-control" id="newsampleparent" name="newsampleparent" type="text" value="">'+
            '</div>'+
            '<div class="form-group ">'+
                '<label class="control-label" for="newsampledescription">Description:</label>'+
                '<textarea class="form-control" id="newsampledescription" name="newsampledescription"></textarea>'+
            '</div>'+
        '</form>'
    );

    this.footer.html('<button id="newsamplesubmit" type="button" class="btn btn-primary">Submit</button>'+
                     '<button id="newsampleclear" type="button" class="btn btn-default">Clear</button>');

    // store DOM elements in variables
    this.newsamplename = this.body.find('#newsamplename').first();
    this.newsampleparent = this.body.find('#newsampleparent').first();
    this.newsampleparentid = this.body.find('#newsampleparentid').first();
    this.newsampledescription = this.body.find('#newsampledescription').first();
    this.newsampleclear = this.footer.find('#newsampleclear').first();
    this.newsamplesubmit = this.footer.find('#newsamplesubmit').first();
    // set up select sample field for parent
    create_selectsample(this.newsampleparent, this.newsampleparentid);
    // set up CKEditor for new sample description
    CKEDITOR.replace(this.newsampledescription[0], ckeditorconfig);

    let this_obj = this;

    this.newsampleclear.click(function(event) {
        event.preventDefault();

        this_obj.newsamplename.val('');
        this_obj.newsampleparent.typeahead('val', '');
        this_obj.newsampleparent.markvalid();
        this_obj.newsampleparentid.val('');
        CKEDITOR.instances['newsampledescription'].setData('');  // TODO: address the specific instance used in this dialog
    });

    this.newsamplesubmit.click(function(event) {
        event.preventDefault();

        var newsampleform = $('#newsampleform');

        // clean up error messages
        newsampleform.find('.form-group').removeClass('has-error');
        newsampleform.find('span.help-block').remove();

        // make sure content of editor is transmitted
        CKEDITOR.instances['newsampledescription'].updateElement(); // TODO: see above

        $.ajax({
            url: "/newsample",
            type: "post",
            data: newsampleform.serialize(),
            success: function(data) {
                if (data.code === 0) {
                    $('#newsample').modal('hide');  // hide and clear the dialog
                    load_sample(data.sampleid);
                    load_navbar();
                } else {
                    // form failed validation; because of invalid data or expired CSRF token
                    for(field in data.error) {
                        if(field === 'csrf_token') {
                            errordialog.showMessage(
                                'The CSRF token has expired. Please reload the page to create a new sample.'
                            );
                            continue;
                        }
                        // get form group
                        var formgroupid = (field !== 'newsampleparentid' ? field : 'newsampleparent');
                        var formgroup = $('#'+formgroupid).closest('.form-group');      // TODO: search only in this dialog
                        // add the has-error to the form group
                        formgroup.addClass('has-error')
                        // add the error message to the form group
                        for(i in data.error[field]) {
                            formgroup.append('<span class="help-block">'+data.error[field][i]+'</span>');
                        }
                    }
                }
            },
            error: function( jqXHR, textStatus ) {
                errordialog.showMessage(
                    'Could not connect to the server. Please make sure you are connected and try again.'
                );
            }
        });
    });

    return this;
}

NewSampleDialog.prototype = Object.create(Dialog.prototype);

NewSampleDialog.prototype.onShow = function () {
    // set the parent field to the current sample
    if(typeof sample_id !== 'undefined') {
        this.newsampleparent.typeahead('val', $('#samplename').text());
        this.newsampleparentid.val(sample_id);
    }
};

NewSampleDialog.prototype.onShown = function() {
    // workaround for a bug in CKEditor -> if we don't do this after the editor is shown, a <br /> tag is inserted
    // if we tab to the editor
    CKEDITOR.instances['newsampledescription'].setData('');   // TODO: address the specific instance used in this dialog

    // put the cursor in the sample name field
    this.newsamplename.focus();
};

NewSampleDialog.prototype.onHide = function() {
    // clear the dialog
    this.newsampleclear.trigger('click');
};