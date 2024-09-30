## v0.3.1

### Bugfixes

* API: fix: ignore deleted users in user list (#252)
* UI: do not show deleted users in shares

### Security patches

* Build(deps): bump werkzeug from 3.0.1 to 3.0.3 (#242)
* Build(deps): bump jinja2 from 3.1.3 to 3.1.4 (#243)
* Build(deps): bump idna from 3.4 to 3.7 (#238)
* Build(deps): bump tqdm from 4.65.0 to 4.66.3 (#241)
* Build(deps): bump pillow from 10.2.0 to 10.3.0 (#237)
* Build(deps): bump requests from 2.31.0 to 2.32.2 (#245)
* Build(deps): bump dnspython from 2.3.0 to 2.6.1 (#239)
* Build(deps-dev): bump black from 23.3.0 to 24.3.0 (#234)
* Build(deps-dev): bump ejs from 3.1.9 to 3.1.10 in /desktop (#240)
* Build(deps): bump cryptography from 42.0.4 to 43.0.1 (#251)
* Build(deps): bump certifi from 2023.7.22 to 2024.7.4 (#250)
* Build(deps): bump authlib from 1.2.0 to 1.3.1 (#246)
* Build(deps-dev): bump rollup from 3.20.7 to 3.29.5 in /js (#254)
* Build(deps): bump urllib3 from 1.26.18 to 1.26.19 (#247)

### CI

* fix fetching of jeditable and bump it to 1.7.3
* CI: docker push: leave the v on the tag
* fix macOS x64 build

### Doc

* add instructions for setup as system service

### Website

* website: add macOS demo app download and detect OS
* Build(deps): bump ws and socket.io in /site (#248)
* Build(deps-dev): bump braces from 3.0.2 to 3.0.3 in /site (#249)
* Build(deps): bump axios and bundlewatch in /site (#256)
* Build(deps): bump body-parser from 1.20.0 to 1.20.3 in /site (#253)

## v0.3.0

### Features

* add link to latest release on help page
* replace "add sample image" by an icon
* add button to clear sample image
* rework header of sample editor (#218)
* use smaller headings on welcome and help page
* more detail in page titles
* center navbar brand on small screens
* remove top navbar controls from login page and improve the login page layout
* add external resources to help
* update UI icons to Font Awesome icons
* update Racine icon and favicon
* run celery tasks synchronously in testing and standalone

### Bugfixes and other improvements

* fix sample search and selection on non-mainview
* log unhandled exceptions app-wide, not only for main blueprint
* log exceptions also in development
* add default error message to AjaxView
* refactor toggle button code
* refactor initialization of R (#217)
* fix: do not initialize hidden CKEditor more than once
* log unauthorized API requests and do not force status to 500
* improve error handling
* improve emailing API spec
* refactor SMB resource API (#209) and user-related API (#215)
* refactor dialog templates
* move generic form methods to base class
* add some API tests for sample and action creation (#213) and fix some pytest warnings (#214)
* do not transmit usage stats in testing
* backend: API refactoring and build improvements
* print: restrict image resizing to print area
* FormDialog: hide modal dialog before showing error dialog
* fix display of recent samples on welcome page
* refactor and clean up templates and CSS
* minify JS
* use more appropriate response codes for mail requests
* refactor icons and add bootstrap and fontawesome icons
* FormDialog: update CKEditor data before serialization
* publish usage stats on startup
* backend refactoring and cleanup
* fix action count in usage stats

### Security patches

* bump cryptography from 41.0.6 to 42.0.4 (#231)
* Bump pillow from 10.0.1 to 10.2.0
* Bump jinja2 from 3.1.2 to 3.1.3

### Desktop standalone demo app

* implement threaded async tasks and simple kv store (#204) and enable email config and usage stats
* bump app-builder-lib and electron-builder in /desktop (#232)
* clean killing of python subprocess at shutdown (#228)
* store data in home dir (#227)
* add standalone executable for x64 and arm64 macOS
* update package.json
* add code signing for macOS and Windows executables
* add some documentation about Desktop app
* Windows: fix welcome page

### Build and CI

* add sonarcloud badge to README
* build: clean up Makefile (#223)
* CI improvements (caching, prebuild app-static, combining builds in one workflow etc.)
* exclude some folders from black and flake8
* Desktop app workflows: fix version determination for pull requests

### devcontainer

* set up file association for jinja templates
* add editor ruler
* add bash-completion

### Website

* bump follow-redirects from 1.15.2 to 1.15.6 in /site (#233)
* bump ip from 2.0.0 to 2.0.1 in /site (#230)
* add testimonial by Everton Arrighi
* add download links for demo apps
* fix website build

## v0.2.0

### Features

* add standalone executable in AppImage and .exe format
  for Linux and Windows platforms
* show last transmitted usage statistics in admin settings

### Bugfixes and other improvements

* replace bootstrap-toc dependency by tocbot
* bump Flask-HTTPAuth from 4.7.0 to 4.8.0
* fix python linting issues (flake8)
* fix JS linting issues (eslint)
* add loading animation for AJAX views
* show API token on user profile
* refactor CSS
* use celery for sending emails
* improve devcontainer setup and automatic server
  reload in development configuration
* remove unused plugin feature

### Security patches

* bump cryptography from 41.0.4 to 41.0.6
* bump pillow from 9.5.0 to 10.0.1
* bump urllib3 from 1.26.15 to 1.26.18
* bump werkzeug from 2.2.3 to 3.0.1
* bump jquery from 1.11.3 to 3.5.1 in /js
* bump tough-cookie from 4.1.2 to 4.1.3 in /js
* bump word-wrap from 1.2.3 to 1.2.5 in /js
* bump semver from 7.5.0 to 7.5.4 in /js

## v0.1.0

* improved version management and release cycle

## v0.0.3

* first release of Racine
