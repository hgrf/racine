import $ from 'jquery';

import AjaxView from './ajaxview';

import MarkAsNewsDialog from '../../dialogs/markasnews';
import UserBrowserDialog from '../../dialogs/userbrowser';
import ConfirmDeleteDialog from '../../dialogs/confirmdelete';

import ckeditorconfig from '../../util/ckeditorconfig';

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

class SampleView extends AjaxView {
  constructor(mainView) {
    super(mainView);
    this.invertactionorder = false;
    this.showparentactions = false;
  }

  onDocumentReady() {
    const self = this;

    new MarkAsNewsDialog();
    new UserBrowserDialog(this.mainView);
    new ConfirmDeleteDialog(function(type, id) {
      switch (type) {
        case 'action':
          R.actionsAPI.deleteAction(id, function(error, data, response) {
            if (!self.#responseHasError(response)) {
              $('#' + id + '.list-entry').remove();
            }
            $('#confirm-delete').modal('hide');
          });
          break;
        case 'sample':
          R.samplesAPI.deleteSample(id, function(error, data, response) {
            if (!self.#responseHasError(response)) {
              self.mainView.loadWelcome();
            }
            $('#confirm-delete').modal('hide');
          });
          break;
        case 'share':
          R.sharesAPI.deleteShare(id, function(error, data, response) {
            if (!self.#responseHasError(response)) {
              $('#sharelistentry' + id).remove();
              if (response.status == 205) { // if the user removed himself from the sharer list
                self.mainView.loadWelcome();
              }
              $('#confirm-delete').modal('hide');
            }
          });
          break;
      }
    });
  }

  load(state, pushState=true, reload=false) {
    state.ajaxView = 'sample';
    state.url = `/editor/${state.sampleid}` +
    `?invertactionorder=${this.invertactionorder}&showparentactions=${this.showparentactions}`;
    state.navUrl = `/sample/${state.sampleid}`;
    super.load(state, pushState, reload);
  }

  confirmUnload(ajax=true, ignore=[], message='') {
    const msg = message ? message : 'Are you sure you want to leave before saving modifications?';
    ignore = ignore.concat(['newsampledescription']);

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

    initEditor(sampleid, this, this.mainView);
    // highlight in tree, if it is already loaded
    if ($(`#nav-entry${sampleid}`).length) {
      $(`#nav-entry${sampleid}`).css('background-color', '#BBBBFF');
      if (!reload) {
        this.mainView.tree.highlight(sampleid, false);
      }
    }
  }

  onLoadError() {
    R.errorDialog(`Sample #${sampleid} does not exist or you do not have access to it.`);
  }

  #responseHasError(response) {
    let errorMsg = null;
    if (!response) {
      errorMsg = 'Server error. Please check your connection.';
    } else if (response.error) {
      if (response.body.message) {
        errorMsg = response.body.message;
      } else {
        errorMsg = response.error;
      }
    }
    if (errorMsg !== null) {
      R.errorDialog(errorMsg);
      return true;
    }
    return false;
  }
}

let hiddeneditor;

function setupSampleImage(sampleid) {
  $('#sampleimage').zoombutton();
  $('#sampleimage').wrap(R.lightboxWrapper);

  // handler for button that changes sample image
  $('#changesampleimage').click(function(event) {
    CKEDITOR.fbtype = 'img';
    CKEDITOR.fbupload = true;
    CKEDITOR.fbcallback = function(url) {
      $.ajax({
        url: `/api/set/sample/image/${sampleid}`,
        type: 'post',
        headers: {'Authorization': 'Bearer ' + R.apiToken},
        data: {'value': url},
        success: function() {
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
                `<img id="sampleimage" src="${url}">` +
              '<img id="changesampleimage" src="/static/images/insertimage.png"' +
                ' title="Change sample image">',
            );
            setupSampleImage(sampleid);
          }
        },
      });
    };
    // use hidden CKEDITOR instance to open the filebrowser dialog
    hiddeneditor.execCommand('fb');
    event.preventDefault();
  });
}

function initEditor(sampleid, sampleview, mainview) {
  if ($('#hiddenckeditor').length) {
    hiddeneditor = CKEDITOR.inline(
        $('#hiddenckeditor')[0],
        $.extend(
            {'removePlugins': 'toolbar,clipboard,pastetext,pastefromword,tableselection,' +
          'widget,uploadwidget,pastefromexcel,uploadimage,uploadfile'},
            ckeditorconfig,
        ),
    );
  }

  // handler for archive button
  $('#archive').click(function() {
    R.samplesAPI.toggleArchived(sampleid, function(error, data, response) {
      if (!response) {
        R.errorDialog('Server error. Please check your connection.');
      } else if (response.error) {
        if (response.body.message) {
          R.errorDialog(response.body.message);
        } else {
          R.errorDialog(response.error);
        }
      } else {
        if (data.isarchived) {
          $('#archive').attr('title', 'De-archive');
          $('#archive').attr('src', '/static/images/dearchive.png');
          $(`#nav-entry${sampleid}`).addClass('nav-entry-archived');
        } else {
          $('#archive').attr('title', 'Archive');
          $('#archive').attr('src', '/static/images/archive.png');
          $(`#nav-entry${sampleid}`).removeClass('nav-entry-archived');
        }
      }
    });
  });

  // handler for collaborative button
  $('#collaborate').click(function() {
    R.samplesAPI.toggleCollaborative(sampleid, function(error, data, response) {
      if (!response) {
        R.errorDialog('Server error. Please check your connection.');
      } else if (response.error) {
        if (response.body.message) {
          R.errorDialog(response.body.message);
        } else {
          R.errorDialog(response.error);
        }
      } else {
        if (data.iscollaborative) {
          $('#collaborate').attr('title', 'Make non-collaborative');
          $('#collaborate').attr('src', '/static/images/non-collaborative.png');
        } else {
          $('#collaborate').attr('title', 'Make collaborative');
          $('#collaborate').attr('src', '/static/images/collaborative.png');
        }
      }
    });
  });

  $('#showinnavigator').click(function() {
    mainview.tree.highlight(sampleid, true);
  });

  $('#scrolltobottom').click(function() {
    $('html, body').stop().animate({scrollTop: $('div#editor-frame').height()}, 1000);
  });

  $('#invertactionorder').click(function() {
    sampleview.invertactionorder = !sampleview.invertactionorder; // toggle
    mainview.loadSample(sampleid, true);
  });

  $('#showparentactions').click(function() {
    sampleview.showparentactions = !sampleview.showparentactions; // toggle
    mainview.loadSample(sampleid, true);
  });

  // handler for new action submit button
  $('#submit').click( function(event) {
    // prevent "normal" submission of form
    event.preventDefault();

    // check if the user is still modifying any actions before submitting the new one
    if (!mainview.ajaxViews.sample.confirmUnload(
        true,
        ['description'],
        'You have been editing the sample description or one or more past actions. Your changes ' +
        'will be lost if you do not save them, are you sure you want to continue?')) {
      return;
    }

    // make sure content of editor is transmitted
    CKEDITOR.instances['description'].updateElement();

    const formdata = {};
    $('#newactionform').serializeArray().map(function(x) {
      formdata[x.name] = x.value;
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
            CKEDITOR.instances.description.setData(event.data.description);
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
      CKEDITOR.instances['description'].destroy();
      mainview.loadSample(sampleid, true);
    });
  });

  // set up the sample image
  setupSampleImage(sampleid);

  $('#sampledescription').racinecontent();
  $('.actiondescription').racinecontent();


  /* Typeset all equations with MathJax. If it is not ready now, it should typeset automatically
   * once it is ready.
   */
  if (typeof(MathJax) !== 'undefined' && MathJax.isReady) {
    MathJax.Hub.Queue(['Typeset', MathJax.Hub]); // eslint-disable-line new-cap
  }

  // set up CKEditor for new action form
  CKEDITOR.replace('description', ckeditorconfig);

  // set up editables (i.e. in-situ editors)

  // add a trigger image to all editables
  $('.editable').setup_triggers();

  // set up editors for sample and action descriptions (CKEditors)
  $('.ckeditable').ckeditable();

  // other editables:
  $('#samplename.editable').texteditable();
  $('#samplename.editable').on('editableupdate', function(event, data) {
    // TODO: data.code is deprecated
    if (!data.code) {
      $(`#nav-entry${sampleid} > .nav-entry-name`).html(data.value);
    }
  });
  $('.actiondate.editable').texteditable();

  $('.swapaction').click( function(event) {
    const element = $(this); // eslint-disable-line no-invalid-this
    R.actionsAPI.swapActionOrder(
        {'actionid': element.data('id'), 'swapid': element.data('swapid')},
        function(error, data, response) {
          if (!response) {
            R.errorDialog('Server error. Please check your connection.');
          } else if (response.error) {
            if (response.body.message) {
              R.errorDialog(response.body.message);
            } else {
              R.errorDialog(response.error);
            }
          } else {
            mainview.loadSample(sampleid, true);
          }
        });
  });

  $('.togglenews').click(function(event) {
    const flag = $(this); // eslint-disable-line no-invalid-this
    const actionid = flag.data('id');

    // is this action not yet marked as news?
    if (flag.hasClass('markasnews')) {
      // set the action ID hidden field
      // TODO: it seems a bit dangerous that this form field is just called "actionid"
      $('#actionid').val(actionid);
      // clear other fields
      $('#title').val('');
      $('#expires').val('');
      $('#dlg_markasnews').modal('show');
    } else {
      R.actionsAPI.unmarkActionAsNews({'actionid': actionid}, function(error, data, response) {
        if (!response) {
          R.errorDialog('Server error. Please check your connection.');
        } else if (response.error) {
          if (response.body.message) {
            R.errorDialog(response.body.message);
          } else {
            R.errorDialog(response.error);
          }
        } else {
          flag.removeClass('unmarkasnews');
          flag.addClass('markasnews');
        }
      });
    }
  });

  $(document).trigger('editor_initialised');
}

export default SampleView;
