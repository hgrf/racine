import LoginView from './login';

/* settings pages */
import EmailView from './email';
import SMBResourcesView from './smbresources';
import UsersView from './users';

/* normal user pages */
import SwaggerUIView from './swagger';
import HelpView from './help';
import LeaveView from './leave';
import PrintView from './print';
import MainView from './main';
import BrowserView from './browser';

const views = {
  login: LoginView,

  main: MainView,

  email: EmailView,
  smbresources: SMBResourcesView,
  users: UsersView,

  swagger: SwaggerUIView,
  help: HelpView,
  print: PrintView,
  leave: LeaveView,

  browser: BrowserView,
};

export default views;
