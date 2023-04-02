(function($){   // this is a jQuery plugin
    $.fn.texteditable = function() {
        // we need to iterate, because if we are given more than one field, the getter/setter functions
        // will be read only once otherwise
        $(this).each(function(index, field) {
            field = $(field);
            field.editable(field.data('setter'), {
                ajaxoptions: {'headers': { 'Authorization': 'Bearer ' + R.apiToken }},
                style: 'inherit',
                event: 'edit',
                placeholder: '&nbsp;',
                callback: function (value, settings) {
                    var json = $.parseJSON(value);
                    field.html(json.value);
                    field.trigger('editableupdate', json);
                    field.trigger('editabledone');
                },
                resetcb: function (value, settings) {
                    field.trigger('editabledone');
                },
                onerror: function(settings, original, xhr) {
                    if(xhr.responseText) {
                        var json = $.parseJSON(xhr.responseText);
                        R.errorDialog(json.message);
                    } else {
                        R.errorDialog("Could not connect to the server. Please make sure you are connected and try again.");
                    }
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
                ajaxoptions: {'headers': { 'Authorization': 'Bearer ' + R.apiToken }},
                data   : choice,
                style  : 'inherit',
                type   : 'select',
                submit : 'OK',
                event  : 'edit',
                callback : function(value, settings) {
                    var json = $.parseJSON(value);
                    field.html(choice[json.value]);
                    field.trigger('editableupdate', json);
                    field.trigger('editabledone');
                },
                resetcb: function(value, settings) {
                    field.trigger('editabledone');
                },
                onerror: function(settings, original, xhr) {
                    if(xhr.responseText) {
                        var json = $.parseJSON(xhr.responseText);
                        R.errorDialog(json.message);
                    } else {
                        R.errorDialog("Could not connect to the server. Please make sure you are connected and try again.");
                    }
                }
            });
        });
    };

    $.fn.ckeditable = function() {
        this.on('edit', ckeditable_activate);
        return this;
    };

    function on_edit_requested(event) {
        if($(this).is('img.edittrigger'))
            field = $(this).parent();
        else
            field = $(this);

        field.unbind('dblclick');
        field.children('img.edittrigger').remove();
        field.addClass('editabling');
        field.removeClass('editable');
        field.trigger('edit');
    }

    $.fn.setup_triggers = function() {
        // add the double click handler
        $(this).unbind("dblclick");
        $(this).dblclick(on_edit_requested);

        // add the edit trigger icon
        $(this).each(function(index, field) {
            field = $(field);
            // we have to iterate because we could not do the if statement on a collection of fields
            if(!field.has('img.edittrigger').length) {
                field.append('<img class="edittrigger" src="/static/images/edit.png">');
            }
            // avoid accumulation of events
            field.find('img.edittrigger').unbind('click');
            field.unbind('editabledone');
            // re-define events
            field.find('img.edittrigger').click(on_edit_requested);
            field.on('editabledone', function (event) {
                field.addClass('editable');
                field.removeClass('editabling');
                field.setup_triggers();
            });
        });
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
            headers: { 'Authorization': 'Bearer ' + R.apiToken },
            success: function( data ) {
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
            },
            error: function( jqXHR, textStatus ) {
                R.errorDialog("Could not connect to the server. Please make sure you are connected and try again.");
                field.trigger('editabledone');
            }
        });
    }

    function ckeditable_on_done(event) {
        editor = event.editor;
        field = event.editor.config.field;
        data = event.editor.getData();

        event.editor.updateElement();

        if(event.data == 'save') {
            $.ajax({
                url: field.data('setter'),
                type: "post",
                headers: { 'Authorization': 'Bearer ' + R.apiToken },
                data: {"value": data},
                success: function( data ) {
                    if(data.code) R.errorDialog("An error occured.");
                    ckeditable_finish(editor, field);
                },
                error: function( jqXHR, textStatus ) {
                    R.errorDialog("Could not connect to the server. Please make sure you are connected and try again.");
                }
            });
        } else {
            ckeditable_finish(editor, field);
        }
    }

    function ckeditable_finish(editor, field) {
        // read new HTML from server (i.e. either the modified or unmodified version)
        $.ajax({
            url: field.data('getter'),
            type: "get",
            headers: { 'Authorization': 'Bearer ' + R.apiToken },
            success: function( data ) {
                editor.destroy();

                // prepare div content for editing
                field.empty();
                field.append(data.value);
                field.attr('contenteditable', false);
                field.removeClass('ckeditabling');

                // typeset all equations in this field
                MathJax.Hub && MathJax.Hub.Queue(["Typeset",MathJax.Hub,field.get()]);

                // catch internal links
                field.find('a').click(function(event) {
                    if(typeof $(this).attr('href') == 'string' && $(this).attr('href').startsWith('/sample/')) {
                        event.preventDefault();
                        R.loadSample($(this).attr('href').split('/')[2]);
                    }
                });

                // put back the zoombutton
                field.find('img').zoombutton();

                // put back lightbox link around images
                field.find('img').wrap(R.lightboxWrapper);

                field.trigger('editableupdate', data);
                field.trigger('editabledone');
            },
            error: function( jqXHR, textStatus ) {
                R.errorDialog("Could not connect to the server. Please make sure you are connected and try again.");
            }
        });
    }
})(jQuery);
