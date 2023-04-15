import $ from "jquery";

import MainView from "./main";

class WelcomeView extends MainView {
    constructor() {
        super();
    }

    load(pushState, state) {
        if(!super.confirmUnload())
            return false;

        // load welcome page
        $.ajax({
            url: "/welcome",
            success: function(data) {
                R.updateState(pushState, state);

                $("#editor-frame").html(data);
                document.title = "Racine";
                R.makeSamplesClickable();
            }
        });

        MainView.tree.load();

        return true;
    }
}

export default WelcomeView;