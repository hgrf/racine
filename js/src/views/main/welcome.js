import AjaxView from "./ajaxview";

class WelcomeView extends AjaxView {
  load(state, pushState=true, reload=false) {
    state.ajaxView = "welcome";
    state.url = "/welcome";
    state.navUrl = "/";
    super.load(state, pushState, reload);
  }

  onLoadSuccess(state, reload) {
    document.title = 'Racine';
    R.makeSamplesClickable();
  }
}

export default WelcomeView;
