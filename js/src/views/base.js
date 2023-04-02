function beforeUnloadHandler(event, ignore, message) {
    var ignore = typeof ignore !== 'undefined' ? ignore : [];
    var msg = typeof message !== 'undefined' ? message : "Are you sure you want to leave before saving modifications?"

    for(var i in CKEDITOR.instances) {
        // first check if the editor is not on the ignore list
        if(ignore.indexOf(i) < 0 && CKEDITOR.instances[i].checkDirty()) {
            if (event !== null)
                event.returnValue = msg;     // Gecko, Trident, Chrome 34+
            return msg;                      // Gecko, WebKit, Chrome <34
        }
    }
}    

function pushCurrentState() {
    // figure out what page we currently have and push state accordingly
    if(typeof sample_id !== "undefined") {
        window.history.pushState({"id": sample_id}, "", "/sample/"+sample_id);
    } else if(typeof term !== "undefined") {
        window.history.pushState({"term": term}, "", "/search?term="+term);
    } else {
        window.history.pushState({},"", "/");
    }
}

function setupBrowserNavigation() {
    // Switch of automatic scroll restoration...
    // so that, if a popstate event occurs but the user does not want to leave the page, automatic scrolling to the top
    // is avoided. However, this means that if we navigate back to some page that was previously scrolled to a specific
    // location, we lose this information and the page is opened at 0 scroll position. This could be solved e.g. by
    // storing the scroll position in the history state variable.
    if ('scrollRestoration' in history) {
        history.scrollRestoration = 'manual';
    }

    // add event handler for history
    window.addEventListener("popstate", function (event) {
        if (event.state != null) {
            var res;
            if (typeof event.state.term !== "undefined") {
                res = R.views.searchResults.load(false, event.state.term);
            } else if (typeof event.state.id !== "undefined") {
                res = R.views.sample.load(false, event.state.id, false, true);
            } else {
                res = R.views.welcome.load(false);
            }
            if (!res)  // the user wants to stay on the page to make modifications
                pushCurrentState();
        }
        else
            location.href = "/";
    });

    // add window unload handler (which asks the user to confirm leaving the page when one of the CKEditor instances
    // has been modified
    window.addEventListener('beforeunload', beforeUnloadHandler);
}

class BaseView {
    constructor() {
    }
    
    confirmUnload(ignore, message) {
        var ignore = typeof ignore !== 'undefined' ? ignore : [];
        ignore = ignore.concat(['newsampledescription']);
    
        // use the beforeUnloadHandler function to check if any CKEditor is being edited
        // if yes, ask the user if he really wants to load a different sample
        var confirm_message = beforeUnloadHandler(null, ignore, message);
        if(confirm_message) {
            if (!confirm(confirm_message)) {
                return false;
            }
        }
        // destroy CKEditors
        for(var i in CKEDITOR.instances) {
            if(ignore.indexOf(i) < 0) {
                CKEDITOR.instances[i].destroy()
            }
        }
        return true;
    }
}

export default BaseView;
export { setupBrowserNavigation };