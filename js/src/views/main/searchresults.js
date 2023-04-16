import AjaxView from './ajaxview';

class SearchResultsView extends AjaxView {
  load(state, pushState=true, reload=false) {
    state.ajaxView = 'searchResults';
    state.url = `/search?ajax=true&${state.term}`;
    state.navUrl = `/search?${state.term}`;
    super.load(state, pushState, reload);
  }

  onDocumentReady() {
    document.title = 'Racine - Search';
    R.makeSamplesClickable();
  }
}

export default SearchResultsView;
