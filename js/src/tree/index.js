import { draggableHandlers, dropZoneHandlers } from "./dragdrop";
import { addGlyphicon } from "./glyphicons";

class Tree {
    constructor() {
        this.orderBy = 'id';
        this.showArchived = false;
    }

    setupHandlers() {
        var activeEntry = $(`#nav-entry${R.state.sampleid}`);
        var allEntries = $('.nav-entry');
        var ctrlIsPressed = false;
        var self = this;
    
        // keep track of CTRL key, so that double click event can open sample in new window if CTRL is held
        $(document).keydown(function(event){
            if(event.which=="17")
                ctrlIsPressed = true;
        });
    
        $(document).keyup(function(event){
            if(event.which=="17")
                ctrlIsPressed = false;
        });
        
        // initialise sample navigation bar double click event
        allEntries.dblclick(function (event) {
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
        allEntries.each(function () { addGlyphicon($(this)); });
    
        // enable sample drag and drop in navigation bar
        allEntries.on(draggableHandlers(activeEntry));
    
        $('.nav-dropzone').on(dropZoneHandlers(activeEntry));
    
        $('.inheritance').dblclick(function() {
           location.href = '/loginas?userid='+$(this).data('userid');
        });
    
        // TODO: togglearchived could now be achieved without reloading the navbar
        $('.navbar-togglearchived').click(function() { 
            self.showArchived = !self.showArchived;
            self.load();
        });
        $('.navbar-sort-az').click(function() {
            self.orderBy = 'name';
            self.load();
        });
        $('.navbar-sort-id').click(function() {
            self.orderBy = 'id';
            self.load();
        });
        $('.navbar-sort-lastmodified').click(function() {
            self.orderBy = 'last_modified';
            self.load();
        });
    }

    // TODO: it would make more sense to define a parameter scroll,
    //       which is either "current", "top", "none" or undefined
    load(scrolltocurrent=false, scrolltotop=false) {
        var self = this;

        $.ajax({
            url: "/navbar",
            data: {'order': self.orderBy,
                'showarchived': self.showArchived},
            success: function(data) {
                // load the navbar
                $('#sidebar').html(data);

                // scroll to top if this was requested
                if(scrolltotop)
                    $('div#sidebar').scrollTop(0);

                if(!self.showArchived) {
                    $('.nav-entry-archived').css('display', 'none');
                    $('.nav-children-archived').css('display', 'none');
                }
            
                // make sure the current sample is highlighted in the navbar (this is redundant in editor.js, but we need to do
                // it here too if editor.js is executed before navbar.js
                if(R.state.view == 'sample') {
                    $('#nav-entry' + R.state.sampleid).css("background-color", "#BBBBFF");
                    if(scrolltocurrent)
                        showInNavbar(R.state.sampleid, false);
                }

                // set up handlers etc.
                self.setupHandlers();
            }
        });
    }
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

export { Tree, showInNavbar };