function initNavbar(scrolltocurrent, scrolltotop) {
    // define default values for arguments
    var scrolltocurrent = typeof scrolltocurrent !== 'undefined' ? scrolltocurrent : true;
    var scrolltotop = typeof scrolltotop !== 'undefined' ? scrolltotop : false;

    if(!showarchived) {
        $('.nav-entry-archived').css('display', 'none');
        $('.nav-children-archived').css('display', 'none');
    }

    // make sure the current sample is highlighted in the navbar (this is redundant in editor.js, but we need to do
    // it here too if editor.js is executed before navbar.js
    if(typeof sample_id !== 'undefined') {
        $('#nav-entry' + sample_id).css("background-color", "#BBBBFF");
        if(scrolltocurrent)
            showInNavbar(sample_id, false);
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

        R.loadSample($(this).data('id'));
        // on small screen, hide the sidebar after a sample has been selected
        R.mobileHideSidebar();
    });

    // add glyphicons to expandable items in the navbar
    $('.nav-entry').each(function () {
        addGlyphicon($(this));
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
            let draggedId = parseInt(event.dataTransfer.getData('sampleid'));
            let parentId = parseInt($(this).data('id'));
            event.preventDefault();
            event.stopPropagation();

            // reset background color (but highlight if sample is active)
            $(this).css("background-color", "transparent");
            $('#nav-entry'+sample_id).css("background-color", "#BBBBFF");

            if(draggedId === parentId) return;

            R.samplesAPI.changeParent(draggedId, parentId, function(error, data, response) {
                if (!response)
                    R.errorDialog("Server error. Please check your connection.");
                else if (response.error) {
                    if (response.body.message)
                        R.errorDialog(response.body.message);
                    else
                        R.errorDialog(response.error);
                } else {
                    let draggedItem = $('#nav-container'+draggedId);
                    let oldParent = draggedItem.parent().prev();
                    if(parentId !== 0) {
                        // moving to a regular nav-entry
                        draggedItem.appendTo('#nav-children'+parentId);
                        updateGlyphicon($('#nav-entry'+parentId));
                    } else {
                        // moving to root
                        draggedItem.appendTo('#nav-mysamples');
                    }
                    if(oldParent.length)        // if it's not the root entry
                        updateGlyphicon(oldParent);
                }
            });
        }
    });

    $('.inheritance').dblclick(function() {
       location.href = '/loginas?userid='+$(this).data('userid');
    });

    // TODO: togglearchived could now be achieved without reloading the navbar
    $('.navbar-togglearchived').click(function() { loadNavbar(order, !showarchived, false); });
    $('.navbar-sort-az').click(function() { loadNavbar('name', showarchived, false); });
    $('.navbar-sort-id').click(function() { loadNavbar('id', showarchived, false); });
    $('.navbar-sort-lastmodified').click(function() {
        loadNavbar('last_modified', showarchived, false);
    });
}

function loadNavbar(_order, _showarchived, scrolltocurrent, scrolltotop) {
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
            initNavbar(scrolltocurrent, scrolltotop);
        }
    });
}

function scrollToSample(id, flash) {
    var naventry = $('#nav-entry'+id);

    if(!naventry.is(':visible')) {
        showarchived = true;
        $('.nav-entry-archived').css('display', 'block');
        $('.nav-children-archived').css('display', 'block');
        $('.navbar-togglearchived').removeClass('glyphicon-eye-close');
        $('.navbar-togglearchived').addClass('glyphicon-eye-open');
        $('.navbar-togglearchived').attr('title', 'Hide archived');
    }

    var top = (naventry.offset().top
        - $('#navbar').height()
        - $('div.navbar-shortcuts').outerHeight()
        - $('html, body').scrollTop());
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

function showInNavbar(id, flash) {
    // make sure all parent samples are expanded in navbar
    var naventry = $('#nav-entry'+id);
    var collapsibles = naventry.parents('.nav-children');
    var collapsed_counter = 0;

    // for each collapsible parent check if it's collapsed and increase the counter accordingly, so that the autoscroll
    // function is only activated when everything has finished expanding (so that the coordinates in scrollToSample
    // are correctly calculated)
    collapsibles.each(function() {
        if($(this).attr('aria-expanded') !== 'true') {   // careful, it can be undefined instead of false, hence the notation
            collapsed_counter++;
            $(this).one('shown.bs.collapse', function() {
                collapsed_counter--;
                if(!collapsed_counter) {
                    scrollToSample(id, flash);
                }
            });
        }
    });

    if(collapsed_counter) {
        collapsibles.collapse('show');
    } else {
        scrollToSample(id, flash);
    }
}

// this function updates the glyphicon as a function of the number of children
function updateGlyphicon(naventry) {
    let glyph = naventry.find('i.glyphicon').first();
    let target = $(naventry.data('target'));

    if (target.children().length > 0) {
        glyph.removeClass('glyphicon-invisible');
        if (target.is(':hidden'))
            glyph.addClass('glyphicon-expand');
        else
            glyph.addClass('glyphicon-collapse-down');

        // change the glyphicons when items are expanded or collapsed
        target.on("show.bs.collapse", function (e) {
            // the event goes up like a bubble and so it can affect parent nav-entries, stop this
            e.stopPropagation();
            glyph.removeClass('glyphicon-expand');
            glyph.addClass('glyphicon-collapse-down');
        });
        target.on("hide.bs.collapse", function (e) {
            e.stopPropagation();
            glyph.addClass('glyphicon-expand');
            glyph.removeClass('glyphicon-collapse-down');
        });
    } else {
        // switch off existing handlers and update classes
        target.off('show.bs.collapse');
        target.off('hide.bs.collapse');
        glyph.removeClass('glyphicon-expand');
        glyph.removeClass('glyphicon-collapse-down');
        glyph.addClass('glyphicon-invisible');
    }
}

// this function adds a glyphicon to naventry
function addGlyphicon(naventry) {
    naventry.prepend('<i class="glyphicon"></i>');
    updateGlyphicon(naventry);
}

export { loadNavbar, showInNavbar };