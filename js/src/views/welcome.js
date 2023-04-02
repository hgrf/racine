import BaseView from "./base";

class WelcomeView extends BaseView {
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

        return true;
    }
}

export default WelcomeView;