import NewSampleDialog from '../../dialogs/newsample';
import Tree from './tree';

import SampleView from './sample';
import SearchResultsView from './searchresults';
import WelcomeView from './welcome';

class MainView {
  constructor(params) {
    this.state = params;
    this.tree = new Tree(this);
    this.ajaxViews = {
      sample: new SampleView(this),
      searchResults: new SearchResultsView(this),
      welcome: new WelcomeView(this),
    };
  }

  curAjaxView() {
    return this.ajaxViews[this.state.ajaxView];
  }

  load(state, pushState=true, reload=false) {
    if (!this.curAjaxView().confirmUnload()) {
      return false;
    }

    this.ajaxViews[state.ajaxView].load(state, pushState, reload);
    return true;
  }

  loadWelcome() {
    this.load({ajaxView: 'welcome'});
  }

  loadSample(id, reload=false) {
    this.load({ajaxView: 'sample', sampleid: id}, true, reload);
  }

  loadSearchResults(query) {
    this.load({ajaxView: 'searchResults', term: query});
  }

  onDocumentReady() {
    this.#setupBrowserNavigation();

    new NewSampleDialog(this, '#newsample');

    for (const view in this.ajaxViews) {
      if (Object.hasOwn(this.ajaxViews, view)) {
        this.ajaxViews[view].onDocumentReady();
      }
    }

    this.tree.load(true);
    this.load(this.state);
  }

  #setupBrowserNavigation() {
    const self = this;

    /* Switch off automatic scroll restoration, so that, if a popstate event occurs but the user
     * does not want to leave the page, automatic scrolling to the top is avoided. However, this
     * means that if we navigate back to some page that was previously scrolled to a specific
     * location, we lose this information and the page is opened at 0 scroll position. This could be
     * solved e.g. by storing the scroll position in the history state variable.
     */
    if ('scrollRestoration' in history) {
      history.scrollRestoration = 'manual';
    }

    // add event handler for history
    window.addEventListener('popstate', function(event) {
      if (event.state != null) {
        if (!self.load(event.state, false)) {
          // the user wants to stay on the page to make modifications
          self.pushCurrentState();
        }
      } else {
        location.href = '/';
      }
    });

    /* add window unload handler (which asks the user to confirm leaving the page when one of the
     * CKEditor instances has been modified
     */
    window.addEventListener('beforeunload', function(event) {
      const msg = 'Are you sure you want to leave before saving modifications?';
      if (!self.curAjaxView(false).confirmUnload()) {
        event.returnValue = msg; // Gecko, Trident, Chrome 34+
        return msg; // Gecko, WebKit, Chrome <34
      }
    });
  }

  pushCurrentState() {
    window.history.pushState(this.state, '', this.state.navUrl);
  }
}

export default MainView;
