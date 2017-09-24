$(document).ready(function() {
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

    // initialise sample navigation bar double click event
    $('.nav-entry').dblclick(function (event) {
        // this is a bit redundant with the TWO other page unload handlers, maybe want to tidy that shit up
        if ($('#sampleid').text() != "" && CKEDITOR.instances.description.checkDirty()) {        // CKEDITOR.instances.description does not exist if no sample is open
            if (confirm('Are you sure you want to navigate away from this page? Press OK to continue, or Cancel to stay on the current page.')) {
                load_sample($(this).attr('id'));
            }
        } else {
            load_sample($(this).attr('id'));
        }
        event.preventDefault();
    });

    // add glyphicons to expandable items in the navbar
    $('.nav-entry').each(function () {
        if ($($(this).data('target')).children().length > 0) {
            addGlyphicon($(this));
        }
    });

    // enable sample drag and drop in navigation bar
    $('.nav-entry').on({
        dragstart: function(event) {
            event.dataTransfer.setData('sampleid', event.target.id);
            event.dataTransfer.setData('text/html', '<a href="/sample/'+event.target.id+'">'+$(event.target).data('name')+'</a> ');
        },
        dragenter: function(event) {
            event.preventDefault();
        },
        dragover: function(event) {
            $(this).css("background-color", "#BBBBFF");
            event.preventDefault();
        },
        dragleave: function(event) {
            $(this).css("background-color", "transparent");
        },
        drop: function(event) {
            var draggedId = event.dataTransfer.getData('sampleid');
            var parentId = $(this).attr('id');
            if(draggedId == parentId) return;
            event.preventDefault();
            $.ajax({
                url: "/changeparent",
                type: "post",
                data: { "id": draggedId, "parent": parentId },
                success: function( data ) {
                    if(data.code==0) {
                        var draggedItem = $( "#"+draggedId+".nav-container" );
                        if(parentId != 0) {
                            if($("#children"+parentId).children().length == 0) {
                                // no children yet, so need to put glyphicon
                                addGlyphicon($("#children"+parentId).prev());
                            }
                            if(draggedItem.parent().children().length == 1) {
                                // there will be no children left after drag/drop, so remove glyphicon
                                removeGlyphicon(draggedItem.parent().prev());
                            }
                            draggedItem.appendTo("#children"+parentId);
                        } else {
                            draggedItem.appendTo("#root");
                        }
                    } else {
                        $( "#flashmessages" ).append(begin_flashmsg+data.error+end_flashmsg);
                    }
                }
            }); // what if we drag parent to child?
            $(this).css("background-color", "transparent");
        }
    });

    $(".inheritance").dblclick(function() {
       location.href = "/loginas?userid="+$(this).data('userid');
    });
});