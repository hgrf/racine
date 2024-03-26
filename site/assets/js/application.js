// NOTICE!! DO NOT USE ANY OF THIS JAVASCRIPT
// IT'S ALL JUST JUNK FOR OUR DOCS!
// ++++++++++++++++++++++++++++++++++++++++++

/*!
 * JavaScript for Bootstrap's docs (https://getbootstrap.com/)
 * Copyright 2011-2022 The Bootstrap Authors
 * Copyright 2011-2022 Twitter, Inc.
 * Licensed under the Creative Commons Attribution 3.0 Unported License.
 * For details, see https://creativecommons.org/licenses/by/3.0/.
 */

function getOs() {
  var os = 'notsup';
  if (window.navigator.userAgent.indexOf('Windows') != -1)
    os = 'win';
  if (window.navigator.userAgent.indexOf('OS X') != -1)
    os = 'osx';
  if (window.navigator.userAgent.indexOf('Linux') != -1)
    os = 'linux';

  return os;
}

const downloadUrl = {
  win: '',
  osx: 'https://github.com/hgrf/racine/releases/download/vXXX/RacineDesktop-XXX.dmg',
  osx_arm64: 'https://github.com/hgrf/racine/releases/download/vXXX/RacineDesktop-XXX-arm64.dmg',
  linux: 'https://github.com/hgrf/racine/releases/download/vXXX/RacineDesktop-XXX.AppImage',
  notsup: 'https://github.com/hgrf/racine/releases/vXXX'
};

const downloadText = {
  win: 'Windows (Installer)',
  osx: 'macOS (x64 .dmg)',
  osx_arm64: 'macOS (arm64 .dmg)',
  linux: 'Linux (AppImage)',
  notsup: 'supported platforms'
};

const downloadIcon = {
  win: 'fab fa-windows',
  osx: 'fab fa-apple',
  osx_arm64: 'fab fa-apple',
  linux: 'fab fa-linux',
  notsup: 'fas fa-download'
};

function makeLink(os, version) {
  return `<a class="link-secondary" href=${downloadUrl[os].replace(/XXX/g, version)}>
      <i class="${downloadIcon[os]}"></i>&nbsp;${downloadText[os]}
      </a>`;
}

(() => {
  'use strict'

  const os = getOs();
  const elms = document.querySelectorAll('div.download-demo');
  for (let i = 0; i < elms.length; i++) {
    const elm = elms[i];
    const version = elm.getAttribute('data-version');
    elm.innerHTML = makeLink(os, version);
    if (os === 'osx') {
      elm.innerHTML += makeLink('osx_arm64', version);
    }
  }

  // Scroll the active sidebar link into view
  const sidenav = document.querySelector('.bd-sidebar')
  if (sidenav) {
    const sidenavHeight = sidenav.clientHeight
    const sidenavActiveLink = document.querySelector('.bd-links-nav .active')
    const sidenavActiveLinkTop = sidenavActiveLink.offsetTop
    const sidenavActiveLinkHeight = sidenavActiveLink.clientHeight
    const viewportTop = sidenavActiveLinkTop
    const viewportBottom = viewportTop - sidenavHeight + sidenavActiveLinkHeight

    if (sidenav.scrollTop > viewportTop || sidenav.scrollTop < viewportBottom) {
      sidenav.scrollTop = viewportTop - (sidenavHeight / 2) + (sidenavActiveLinkHeight / 2)
    }
  }
})()
