import LoginView from './login';

import SampleView from './main/sample';
import SearchResultsView from './main/searchresults';
import WelcomeView from './main/welcome';

import SMBResourcesView from './smbresources';
import UsersView from './users';

import HelpView from './help';
import LeaveView from './leave';
import PrintView from './print';

const views = {
    login: new LoginView(),

    sample: new SampleView(),
    searchResults: new SearchResultsView(),
    welcome: new WelcomeView(),

    smbresources: new SMBResourcesView(),
    users: new UsersView(),

    help: new HelpView(),
    print: new PrintView(),
    leave: new LeaveView(),
};

export default views;