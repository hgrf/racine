import $ from 'jquery';

import R from '../../racine';

import AjaxView from './ajaxview';

import MarkAsNewsDialog from '../../dialogs/markasnews';
import UserBrowserDialog from '../../dialogs/userbrowser';
import ConfirmDeleteDialog from '../../dialogs/confirmdelete';

import ckeditorconfig from '../../util/ckeditorconfig';

import icons from '../../util/icons';

/* Disable caching for AJAX requests.
 * This fixes a bug in Internet Explorer, e.g. when reloading the sample
 * after adding an action, the new action is not shown / when modifying an
 * action, the old action is shown after saving, even though the data has
 * been updated on the server.
 *
 * c.f. https://www.itworld.com/article/2693447/ajax-requests-not-executing
-or-updating-in-internet-explorer-solution.html
 */
$.ajaxSetup({cache: false});

class ToggleButton {
  constructor(selector, icon, title, initialState, callback) {
    this.selector = selector;
    this.icon = icon;
    this.title = title;

    this.button = $(selector);

    if (icon.common) {
      this.button.addClass(icon.common);
    }

    if (icon.activeSub || icon.inactiveSub) {
      this.button.append(`<i class='${icon.common}'></i>`);
    }

    this.subIcon = this.button.children('i');

    this.setState(initialState);
    this.button.on('click', callback);
  }

  setState(state) {
    this.state = state;

    if (state) {
      this.button.attr('title', this.title.active);
      this.button.removeClass(this.icon.inactive);
      this.button.addClass(this.icon.active);

      if (this.icon.activeSub && this.icon.inactiveSub) {
        this.subIcon.removeClass(this.icon.inactiveSub);
        this.subIcon.addClass(this.icon.activeSub);
      }
    } else {
      this.button.attr('title', this.title.inactive);
      this.button.removeClass(this.icon.active);
      this.button.addClass(this.icon.inactive);

      if (this.icon.activeSub && this.icon.inactiveSub) {
        this.subIcon.removeClass(this.icon.activeSub);
        this.subIcon.addClass(this.icon.inactiveSub);
      }
    }
  }
}

class SampleView extends AjaxView {
  constructor(mainView) {
    super(mainView);
    this.invertactionorder = false;
    this.showparentactions = false;
    this.hiddenEditor = null;
  }

  onDocumentReady() {
    const self = this;

    this.dlgMarkAsNews = new MarkAsNewsDialog();
    new UserBrowserDialog(() => this.mainView.state.sampleid);
    new ConfirmDeleteDialog({
      'action': (id) => {
        R.actionsAPI.deleteAction(id, (error, data, response) => {
          if (!R.responseHasError(response)) {
            $(`#${id}.list-entry`).remove();
          }
        });
      },
      'sample': (id) => {
        R.samplesAPI.deleteSample(id, (error, data, response) => {
          if (!R.responseHasError(response)) {
            $(`#nav-entry${id}`).remove();
            self.mainView.loadWelcome();
          }
        });
      },
      'share': (id) => {
        R.sharesAPI.deleteShare(id, (error, data, response) => {
          if (!R.responseHasError(response)) {
            $(`#sharelistentry${id}`).remove();
            if (response.status == 205) {
            /* if the user removed himself from the sharer list, remove the item from the
                 * tree and load the welcome page
                 */
              $(`#nav-entry${self.mainView.state.sampleid}`).remove();
              self.mainView.loadWelcome();
            }
          }
        });
      },
    });
  }

  load(state, pushState=true, reload=false) {
    state.ajaxView = 'sample';
    state.url = `/aview/editor/${state.sampleid}` +
    `?invertactionorder=${this.invertactionorder}&showparentactions=${this.showparentactions}`;
    state.navUrl = `/sample/${state.sampleid}`;
    super.load(state, pushState, reload);
  }

  confirmUnload(ajax=true, ignore=[], message='') {
    const msg = message ? message : 'Are you sure you want to leave before saving modifications?';
    ignore = ignore.concat(['new-sample-description']);

    for (const i in CKEDITOR.instances) {
      // check if the editor is not in the ignore list and has modifications
      if (ignore.indexOf(i) < 0 && CKEDITOR.instances[i].checkDirty()) {
        // if the confirmation request is related to an AJAX call, show a dialog
        if (ajax) {
          if (!confirm(msg)) {
            return false;
          }
          // if the confirmation request is related to a page reload or close, just return false
        } else {
          return false;
        }
        break;
      }
    }

    // destroy CKEditors
    for (const i in CKEDITOR.instances) {
      if (ignore.indexOf(i) < 0) {
        CKEDITOR.instances[i].destroy();
      }
    }

    $(`#nav-entry${this.mainView.state.sampleid}`).css('background-color', 'transparent');

    return true;
  }

  onLoadSuccess(state, reload) {
    const sampleid = state.sampleid;

    document.title = 'Racine - '+$('#samplename').text();

    this.#setupView(sampleid);

    // highlight in tree, if it is already loaded
    if ($(`#nav-entry${sampleid}`).length) {
      $(`#nav-entry${sampleid}`).css('background-color', '#BBBBFF');
      if (!reload) {
        this.mainView.tree.highlight(sampleid, false);
      }
    }
  }

  onLoadError(state) {
    R.errorDialog(`Sample #${state.sampleid} does not exist or you do not have access to it.`);
  }

  #setupView(sampleid) {
    this.#setupHeader(sampleid);
    this.#setupActions(sampleid);

    // set up new action form
    CKEDITOR.replace('new-action-description', ckeditorconfig);
    $('#new-action-submit').on('click', this.onActionSubmit.bind(this));

    // Typeset equations with MathJax. If it is not ready now, typeset once it is ready.
    if (typeof(MathJax) !== 'undefined' && MathJax.isReady) {
      MathJax.Hub.Queue(['Typeset', MathJax.Hub]); // eslint-disable-line new-cap
    }

    // add a trigger image to all editables
    $('.editable').setup_triggers();

    // set up editors for sample and action descriptions (CKEditors)
    $('.ckeditable').ckeditable();

    $(document).trigger('editor_initialised');
  }

  #setupHeader(sampleid) {
    this.#setupSampleImage(sampleid);
    $('#samplename.editable').texteditable();
    $('#samplename.editable').on('editableupdate', function(event, data) {
      $(`#nav-entry${sampleid} > .nav-entry-name`).html(data.value);
    });
    $('#sampledescription').racinecontent();
    this.#setupTopRightButtons(sampleid);
  }

  #setupTopRightButtons(sampleid) {
    const self = this;
    const mV = this.mainView;

    const btnArchive = new ToggleButton(
      '#archive',
      icons.btnArchive,
      {active: 'De-archive', inactive: 'Archive'},
      $('#sampleattributes').data('isarchived') === 'True',
      function() {
        R.samplesAPI.toggleArchived(sampleid, function(error, data, response) {
          if (!R.responseHasError(response)) {
            btnArchive.setState(data.isarchived);
            if (data.isarchived) {
              $(`#nav-entry${sampleid}`).addClass('nav-entry-archived');
            } else {
              $(`#nav-entry${sampleid}`).removeClass('nav-entry-archived');
            }
          }
        });
      }
    );

    const btnCollaborate = new ToggleButton(
      '#collaborate',
      icons.btnCollaborate,
      {active: 'Make non-collaborative', inactive: 'Make collaborative'},
      $('#sampleattributes').data('iscollaborative') === 'True',
      function() {
        R.samplesAPI.toggleCollaborative(sampleid, function(error, data, response) {
          if (!R.responseHasError(response)) {
            btnCollaborate.setState(data.iscollaborative);
          }
        });
      }
    );

    new ToggleButton(
      '#showparentactions',
      icons.btnShowParentActions,
      {active: 'Hide parent actions', inactive: 'Show parent actions'},
      self.showparentactions,
      function() {      
        self.showparentactions = !self.showparentactions;
        mV.loadSample(sampleid, true);
      }
    );

    $('#showinnavigator').on('click', () => {
      mV.tree.highlight(sampleid, true);
    });

    $('#scrolltobottom').on('click', function() {
      $('html, body').stop().animate({scrollTop: $('div#editor-frame').height()}, 1000);
    });

    $('#invertactionorder').on('click', function() {
      self.invertactionorder = !self.invertactionorder;
      mV.loadSample(sampleid, true);
    });
  }

  #setupActions(sampleid) {
    const self = this;
    const mV = this.mainView;

    $('.actiondescription').racinecontent();
    $('.actiondate.editable').texteditable();

    $('.swapaction').on('click', function(event) {
      const element = $(this); // eslint-disable-line no-invalid-this
      R.actionsAPI.swapActionOrder(
          {'actionid': element.data('id'), 'swapid': element.data('swapid')},
          function(error, data, response) {
            if (!R.responseHasError(response)) {
              mV.loadSample(sampleid, true);
            }
          });
    });

    $('.togglenews').on('click', function(event) {
      const flag = $(this); // eslint-disable-line no-invalid-this
      const actionid = flag.data('id');

      // is this action not yet marked as news?
      if (flag.hasClass('markasnews')) {
        self.dlgMarkAsNews.show(actionid);
      } else {
        R.actionsAPI.unmarkAsNews(actionid, function(error, data, response) {
          if (!R.responseHasError(response)) {
            flag.removeClass('unmarkasnews');
            flag.addClass('markasnews');
          }
        });
      }
    });
  }

  #setupSampleImage(sampleid) {
    const self = this;

    $('#sampleimage').zoombutton();
    $('#sampleimage').lightbox();

    if (self.hiddenEditor === null && $('#hiddenckeditor').length) {
      self.hiddenEditor = CKEDITOR.inline(
          $('#hiddenckeditor')[0],
          $.extend(
              {'removePlugins': 'toolbar,clipboard,pastetext,pastefromword,tableselection,' +
            'widget,uploadwidget,pastefromexcel,uploadimage,uploadfile'},
              ckeditorconfig,
          ),
      );
    }

    $('#changesampleimage').on('click', function(event) {
      CKEDITOR.fbtype = 'img';
      CKEDITOR.fbupload = true;
      CKEDITOR.fbcallback = function(url) {
        R.fieldsAPI.setField('sample', sampleid, 'image', {'value': url}, (err, data, response) => {
          // check if there is currently a sample image
          if ($('#sampleimage').length) {
            // update the sample image
            $('#sampleimage').attr('src', url);
          } else {
            // add sample image and remove "add sample image" link
            const div = $('div.newsampleimage');
            div.removeClass('newsampleimage');
            div.addClass('imgeditable');
            div.empty();
            /* TODO: this is duplicated code from templates/main/sample.html, there is probably a
              *       more elegant way to sort this out
              */
            div.append(
                `<img id="sampleimage" src="${url}">
                <i id="changesampleimage" class="${icons.changeImage}" title="Change sample image">
                </i>`,
            );
            self.#setupSampleImage(sampleid);
          }
        });
      };
      // use hidden CKEDITOR instance to open the filebrowser dialog
      self.hiddenEditor.execCommand('fb');
      event.preventDefault();
    });
  }

  onActionSubmit(event) {
    event.preventDefault();

    const mV = this.mainView;
    const sampleid = mV.state.sampleid;

    // check if the user is still modifying any actions before submitting the new one
    if (!mV.ajaxViews.sample.confirmUnload(
        true,
        ['new-action-description'],
        'You have been editing the sample description or one or more past actions. Your changes ' +
        'will be lost if you do not save them, are you sure you want to continue?')) {
      return;
    }

    // make sure content of editor is transmitted
    CKEDITOR.instances['new-action-description'].updateElement();

    const formdata = {};
    $('#newactionform').serializeArray().map(function(x) {
      const prefix = 'new-action-';
      formdata[x.name.startsWith(prefix) ? x.name.slice(prefix.length) : x.name] = x.value;
    });

    R.actionsAPI.createAction(sampleid, formdata, function(error, data, response) {
      if (!response) {
        R.errorDialog('Server error. Please check your connection.');
      } else if (response.error) {
        if (response.body.resubmit) {
          // form failed validation; because of invalid data or expired CSRF token
          // we still reload the sample in order to get a new CSRF token, but we
          // want to keep the text that the user has written in the description field
          $(document).one('editor_initialised', formdata, function(event) {
            CKEDITOR.instances['new-action-description'].setData(event.data.description);
            R.errorDialog('Form is not valid. Either you entered an invalid date ' +
                                      'or the session has expired. Try submitting again.');
          });
        } else {
          R.errorDialog(response.error);
          return;
        }
      }

      // reload the sample
      // TODO: it would be sufficient to just add the new action
      // destroy it so that it doesn't bother us with confirmation dialogs when we
      // reload the sample
      CKEDITOR.instances['new-action-description'].destroy();
      mV.loadSample(sampleid, true);
    });
  }
}

export default SampleView;
