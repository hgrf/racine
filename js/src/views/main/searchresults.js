import AjaxView from './ajaxview';

class SearchResultsView extends AjaxView {
  load(state, pushState=true, reload=false) {
    state.ajaxView = 'searchResults';
    state.url = `/search?ajax=true&term=${state.term}`;
    state.navUrl = `/search?term=${state.term}`;
    super.load(state, pushState, reload);
  }

  onLoadSuccess(state, reload) {
    document.title = 'Racine - Search';
    R.makeSamplesClickable();
  }
}

export default SearchResultsView;
