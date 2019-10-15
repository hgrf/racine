$(document).ready(function() {
    var order = 'id';
    var showarchived = false;

    // default load with order by ID and hide archived samples
    load_navbar(order, false);

    function init_navbar() {
        // make sure the current sample is highlighted in the navbar (this is redundant in editor.js, but we need to do
        // it here too if editor.js is executed before navbar.js
        if(typeof sample_id !== 'undefined') {
            $('#nav-entry' + sample_id).css("background-color", "#BBBBFF");
            show_in_navbar(sample_id, false);
        }

        // keep track of CTRL key, so that double click event can open sample in new window if CTRL is held
        $(document).keydown(function(event){
            if(event.which=="17")
                ctrlIsPressed = true;
        });

        $(document).keyup(function(event){
            if(event.which=="17")
                ctrlIsPressed = false;
        });

        var ctrlIsPressed = false;

        // initialise sample navigation bar double click event
        $('.nav-entry').dblclick(function (event) {
            event.preventDefault();

            // if CTRL is pressed, open sample in a new tab
            if(ctrlIsPressed) {
                window.open('/sample/' + $(this).data('id'));
                return;
            }

            // use the before_unload_handler function in editor.js to check if any CKEditor is being edited
            // if yes, ask the user if he really wants to load a different sample
            confirm_message = before_unload_handler(0);
            if(confirm_message) {
                if (confirm(confirm_message)) {
                    load_sample($(this).data('id'));
                }
            } else {
                load_sample($(this).data('id'));
            }
            mobile_hide_sidebar();   // on the small screen, hide the sidebar after a sample has been selected
        });

        // add glyphicons to expandable items in the navbar
        $('.nav-entry').each(function () {
            if ($($(this).data('target')).children().length > 0) {
                addGlyphicon($(this));
            }
        });

        // enable sample drag and drop in navigation bar
        $('.nav-entry').on({
            dragstart: function (event) {
                event.dataTransfer.setData('sampleid', $(event.target).data('id'));
                event.dataTransfer.setData('text/html', '<a href="/sample/' + $(event.target).data('id') + '">' + $(event.target).data('name') + '</a> ');
            }
        });

        $('.nav-dropzone').on({
            dragenter: function(event) {
                event.preventDefault();
                event.stopPropagation();
            },
            dragover: function(event) {
                $(this).css("background-color", "#BBBBFF");
                event.preventDefault();
                event.stopPropagation();
            },
            dragleave: function(event) {
                $(this).css("background-color", "transparent");
            },
            drop: function(event) {
                var draggedId = event.dataTransfer.getData('sampleid');
                var parentId = $(this).data('id');
                if(draggedId == parentId) return;
                event.preventDefault();
                event.stopPropagation();
                $.ajax({
                    url: "/changeparent",
                    type: "post",
                    data: { "id": draggedId, "parent": parentId },
                    success: function( data ) {
                        if(data.code==0) {
                            var draggedItem = $( "#nav-container"+draggedId );
                            if(draggedItem.parent().children().length == 1) {
                                // there will be no children left after drag/drop, so remove glyphicon
                                removeGlyphicon(draggedItem.parent().prev());
                            }
                            if(parentId != '0') {
                                // moving to a regular nav-entry
                                draggedItem.appendTo("#nav-children" + parentId);
                                if ($("#children" + parentId).children().length == 0) {
                                    // no children yet, so need to put glyphicon
                                    addGlyphicon($("#nav-children" + parentId).prev());
                                }
                            } else {
                                // moving to root
                                draggedItem.appendTo("#nav-mysamples");
                            }
                        } else {
                            $( "#flashmessages" ).append(begin_flashmsg+data.error+end_flashmsg);
                        }
                    }
                }); // what if we drag parent to child?
                $(this).css("background-color", "transparent");
            }
        });

        $('.inheritance').dblclick(function() {
           location.href = '/loginas?userid='+$(this).data('userid');
        });

        $('.navbar-togglearchived').click(function(event) { load_navbar(order, !showarchived); });
        $('.navbar-sort-az').click(function(event) { load_navbar('name', showarchived); });
        $('.navbar-sort-id').click(function(event) { load_navbar('id', showarchived); });
        $('.navbar-sort-lastaction').click(function(event) { load_navbar('last_action_date', showarchived); });
    }

    function load_navbar(_order, _showarchived) {
        order = _order;
        showarchived = _showarchived;

        $.ajax({
            url: "/navbar",
            data: {'order': order,
                   'showarchived': showarchived},
            success: function(data) {
                // load the navbar
                $('#sidebar').html(data);

                // set up handlers etc.
                init_navbar();
            }
        });
    }

    // this function adds a glyphicon to the nav-entry $target
    function addGlyphicon($target) {
        if ($($target.data('target')).is(":hidden"))
            $target.prepend('<span class="glyphicon glyphicon-expand"></span>');
        else
            $target.prepend('<span class="glyphicon glyphicon-collapse-down"></span>');

        // change the glyphicons when items are expanded or collapsed
        $($target.data('target')).on("show.bs.collapse", function (e) {
            // the event goes up like a bubble and so it can affect parent nav-entries, if we do not pay
            // attention where the event comes from
            if ($(this).attr('id') != e.target.id)
                return;
            // $(this) now corresponds to the children container, we need to access the corresponding
            // nav-entry using $(this).prev()
            $(this).prev().children('.glyphicon').remove();
            $(this).prev().prepend('<span class="glyphicon glyphicon-collapse-down"></span>');
        });
        $($target.data('target')).on("hide.bs.collapse", function (e) {
            if ($(this).attr('id') != e.target.id)
                return;
            $(this).prev().children('.glyphicon').remove();
            $(this).prev().prepend('<span class="glyphicon glyphicon-expand"></span>');
        });
    }

    function removeGlyphicon($target) {
        $target.children('.glyphicon').remove();
        $($target.data('target')).off('show.bs.collapse');
        $($target.data('target')).off('hide.bs.collapse');
    }
});