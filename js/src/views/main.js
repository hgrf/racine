import BaseView from "./base";

import NewSampleDialog from "../dialogs/newsample";
import Tree from "../tree";

class MainView extends BaseView {
    // subclasses of MainView (WelcomeView, SampleView, SearchResultsView)
    // all share the same tree instance
    static tree = new Tree();

    constructor() {
        super();
    }

    onDocumentReady() {
        new NewSampleDialog('#newsample');

        MainView.tree.load(true);
    }
}

export default MainView;