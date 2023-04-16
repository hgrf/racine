import LoginView from './login';

import SMBResourcesView from './smbresources';
import UsersView from './users';

import HelpView from './help';
import LeaveView from './leave';
import PrintView from './print';
import MainView from './main';

const views = {
    login: LoginView,

    main: MainView,

    smbresources: SMBResourcesView,
    users: UsersView,

    help: HelpView,
    print: PrintView,
    leave: LeaveView,
};

export default views;