(function($){
    function on_trigger_image(event) {
        field = $(this).parent();

        field.addClass('editabling');
        field.removeClass('editable');
        field.trigger('dblclick');
    }

    $.fn.add_trigger_image = function() {
        fields = $(this);

        fields.append('<img class="edittrigger" src="/static/edit.png">');
        fields.find('img.edittrigger').click(on_trigger_image);
        fields.on('editableupdate', function (event) {
            fields.addClass('editable');
            fields.removeClass('editabling');
            if(!fields.has('img.edittrigger').length)
                fields.add_trigger_image();
        });
        return this;
    };


    $.fn.texteditable = function() {
        // we need to iterate, because if we are given more than one field, the getter/setter functions
        // will be read only once otherwise
        $(this).each(function(index, field) {
            field = $(field);
            field.editable(field.data('setter'), {
                style: 'inherit',
                event: 'dblclick',
                width: '10ex',
                loadurl: field.data('getter'),
                callback: function (value, settings) {
                    var json = $.parseJSON(value);
                    field.html(json.value);
                    // display error message if error occured
                    if (json.code)
                        $("#flashmessages").append(begin_flashmsg + data.message + end_flashmsg);
                    field.trigger('editableupdate', json);
                }
            });
        });
    };

    $.fn.comboeditable = function(choice) {
        // we need to iterate, because if we are given more than one field, the getter/setter functions
        // will be read only once otherwise
        $(this).each(function(index, field) {
            field = $(field);
            field.editable(field.data('setter'), {
                data   : choice,
                style  : 'inherit',
                type   : 'select',
                submit : 'OK',
                event  : 'dblclick',
                callback : function(value, settings) {
                    var json = $.parseJSON(value);
                    field.html(choice[json.value]);
                    // display error message if error occured
                    if(json.code)
                        $( "#flashmessages" ).append(begin_flashmsg+data.message+end_flashmsg);
                    field.trigger('editableupdate', json);
                }
            });
        });
    };

    $.fn.ckeditable = function() {
        this.dblclick(ckeditable_activate);
        return this;
    };

    function ckeditable_activate(event) {
        // do not react if the user clicked on an image
        if($(event.target).is('img'))
            return;

        field = $(this);

        // read original HTML from server in order to remove all modifications like Latex parsing or Lightbox
        $.ajax({
            url: field.data('getter'),
            type: 'get',
            indexvalue: $(this),            // a little trick to pass the element to the success function
            success: function( data ) {
                // remove click handler from field
                field.off('dblclick');

                // prepare div content for editing
                field.empty();
                field.append(data.value);
                field.attr('contenteditable', true);
                field.addClass('ckeditabling');

                // prepare settings for CKEditor
                var clone = $.extend({}, ckeditorconfig); // clone main settings
                clone.startupFocus = true;
                clone.field = field;

                // activate CKEditor
                editor = CKEDITOR.inline(field.get()[0], clone);
                editor.on('done', ckeditable_on_done);
            }
        });
    }

    function ckeditable_on_done(event) {
        field = event.editor.config.field;
        data = event.editor.getData();

        event.editor.updateElement();
        event.editor.destroy();

        if(event.data == 'save') {
            $.ajax({
                url: field.data('setter'),
                type: "post",
                data: {"value": data},
                success: function( data ) {
                    if(data.code) alert("An error occured.");
                    ckeditable_finish(field);
                }
            });
        } else {
            ckeditable_finish(field);
        }
    }

    function ckeditable_finish(field) {
        // read new HTML from server (i.e. either the modified or unmodified version)
        $.ajax({
            url: field.data('getter'),
            type: "get",
            success: function( data ) {
                // but click handler back to field
                field.dblclick(ckeditable_activate);

                // prepare div content for editing
                field.empty();
                field.append(data.value);
                field.attr('contenteditable', false);
                field.removeClass('ckeditabling');

                // typeset all equations in this field
                MathJax.Hub && MathJax.Hub.Queue(["Typeset",MathJax.Hub,field.get()]);

                // put back lightbox link around images
                field.find('img').wrap(function() { return '<a class="lightboxlink" href="'+this.src+'" data-lightbox="'+sample_id+'">'; });

                field.trigger('editableupdate');
            }
        });
    }
})(jQuery);
