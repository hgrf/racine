import BaseView from "./base";

class SearchResultsView extends BaseView {
    constructor() {
        super();
    }

    load(pushState, term) {
        if(!R.confirmUnload())
            return false;

        $.ajax({
            url: "/search?ajax=true&term="+term,
            success: function(data) {
                // if currently viewing a sample (not welcome page) then change the navbar background to transparent
                if(typeof sample_id !== "undefined")
                    $('#nav-entry' + sample_id).css("background-color", "transparent");
                sample_id = undefined;

                if(pushState)
                    window.history.pushState({"term": term}, "", "/search?term="+term);
                document.title = "Racine - Search";

                $("#editor-frame").html(data);
                R.makeSamplesClickable();
            }
        });

        return true;
    }
}

export default SearchResultsView;