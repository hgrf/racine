var order;
var showarchived;

function init_navbar(scrolltocurrent, scrolltotop) {
    // define default values for arguments
    var scrolltocurrent = typeof scrolltocurrent !== 'undefined' ? scrolltocurrent : true;
    var scrolltotop = typeof scrolltotop !== 'undefined' ? scrolltotop : false;

    // make sure the current sample is highlighted in the navbar (this is redundant in editor.js, but we need to do
    // it here too if editor.js is executed before navbar.js
    if(typeof sample_id !== 'undefined') {
        $('#nav-entry' + sample_id).css("background-color", "#BBBBFF");
        if(scrolltocurrent)
            show_in_navbar(sample_id, false);
    }

    // scroll to top if this was requested
    if(scrolltotop)
        $('div#sidebar').scrollTop(0);

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

        load_sample($(this).data('id'));
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
        },
        drop: function(event) {
            // reset background color (but highlight if sample is active)
            $(this).css("background-color", "transparent");
            $('#nav-entry'+sample_id).css("background-color", "#BBBBFF");
        }
    });

    $('.nav-dropzone').on({
        dragenter: function(event) {
            event.preventDefault();
            event.stopPropagation();
        },
        dragover: function(event) {
            $(this).css("background-color", "#CCCCEE");
            event.preventDefault();
            event.stopPropagation();
        },
        dragleave: function(event) {
            // reset background color (but highlight if sample is active)
            $(this).css("background-color", "transparent");
            $('#nav-entry'+sample_id).css("background-color", "#BBBBFF");
        },
        drop: function(event) {
            var draggedId = event.dataTransfer.getData('sampleid');
            var parentId = $(this).data('id');
            event.preventDefault();
            event.stopPropagation();

            // reset background color (but highlight if sample is active)
            $(this).css("background-color", "transparent");
            $('#nav-entry'+sample_id).css("background-color", "#BBBBFF");

            if(draggedId == parentId) return;

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
                        error_dialog(data.error);
                    }
                }
            });
        }
    });

    $('.inheritance').dblclick(function() {
       location.href = '/loginas?userid='+$(this).data('userid');
    });

    $('.navbar-togglearchived').click(function(event) { load_navbar(order, !showarchived, false); });
    $('.navbar-sort-az').click(function(event) { load_navbar('name', showarchived, false); });
    $('.navbar-sort-id').click(function(event) { load_navbar('id', showarchived, false); });
    $('.navbar-sort-lastaction').click(function(event) {
        load_navbar('last_action_date', showarchived, false);
    });
}

function load_navbar(_order, _showarchived, scrolltocurrent, scrolltotop) {
    // define default values for arguments
    order = typeof _order !== 'undefined' ? _order : order;
    showarchived = typeof _showarchived !== 'undefined' ? _showarchived : showarchived;
    // TODO: it would make more sense to define a parameter scroll,
    //       which is either "current", "top", "none" or undefined
    var scrolltocurrent = typeof scrolltocurrent !== 'undefined' ? scrolltocurrent : true;
    var scrolltotop = typeof scrolltotop !== 'undefined' ? scrolltotop : false;

    $.ajax({
        url: "/navbar",
        data: {'order': order,
               'showarchived': showarchived},
        success: function(data) {
            // load the navbar
            $('#sidebar').html(data);

            // set up handlers etc.
            init_navbar(scrolltocurrent, scrolltotop);
        }
    });
}

function scroll_to_sample(id, flash) {
    var naventry = $('#nav-entry'+id);

    if(!naventry.is(':visible')) {
        console.error('cannot scroll to hidden sample');
        return;
    }

    var top = naventry.offset().top-$('#navbar').height()-$('html, body').scrollTop();
    var isInView = top >= 0 && top+naventry.outerHeight() <= $('div#sidebar').outerHeight();
    if(!isInView) {
        $('div#sidebar')
            .stop()
            .animate({scrollTop: top + $('div#sidebar').scrollTop()}, 1000);
    }
    if(flash) {
        var old_background = naventry.css("background-color");
        // flash the sample
        naventry
            .stop()
            .delay(isInView ? 0 : 1000)
            .queue(function (next) {
                $(this).css("background-color", "#FFFF9C");
                next();
            })
            .delay(1000)
            .queue(function (next) {
                $(this).css("background-color", old_background);
                next();
            });
    }
}

function show_in_navbar(id, flash) {
    // make sure all parent samples are expanded in navbar
    var naventry = $('#nav-entry'+id);
    var collapsibles = naventry.parents('.nav-children');
    var collapsed_counter = 0;

    // for each collapsible parent check if it's collapsed and increase the counter accordingly, so that the autoscroll
    // function is only activated when everything has finished expanding (so that the coordinates in scroll_to_sample
    // are correctly calculated)
    collapsibles.each(function() {
        if($(this).attr('aria-expanded') !== 'true') {   // careful, it can be undefined instead of false, hence the notation
            collapsed_counter++;
            $(this).one('shown.bs.collapse', function() {
                collapsed_counter--;
                if(!collapsed_counter) {
                    scroll_to_sample(id, flash);
                }
            });
        }
    });

    if(collapsed_counter) {
        collapsibles.collapse('show');
    } else {
        scroll_to_sample(id, flash);
    }
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

$(document).ready(function() {
    order = 'id';
    showarchived = false;

    // default load with order by ID and hide archived samples
    load_navbar(order, false);
});