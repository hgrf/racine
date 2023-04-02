function loadWelcome(pushstate) {
    if(!R.confirmUnload())
        return false;

    // load welcome page
    $.ajax({
        url: "/welcome",
        success: function(data) {
            // if currently viewing a sample (not welcome page) then change the navbar background to transparent
            if(typeof sample_id !== "undefined")
                $('#nav-entry' + sample_id).css("background-color", "transparent");
            sample_id = undefined;
            term = undefined;

            if(pushstate)
                window.history.pushState({},"", "/");
            document.title = "Racine";

            $("#editor-frame").html(data);
            R.makeSamplesClickable();
        }
    });

    return true;
}

export default loadWelcome;