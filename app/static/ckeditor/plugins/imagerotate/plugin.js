'use strict';

(function () {
  var TO_RADIANS = Math.PI / 180;

  CKEDITOR.plugins.add('imagerotate', {
    lang: 'en,et',
    hidpi: true,
    icons: 'rotate-left.png,rotate-right.png', // is this line necessary?
    init: function (editor) {

      editor.addCommand('rotateLeft', {
        exec: function (editor) {
          rotateSelectedImageByAngle(editor, -90);
        }
      });

      editor.addCommand('rotateRight', {
        exec: function (editor) {
          rotateSelectedImageByAngle(editor, 90);
        }
      });

      var translations = editor.lang.imagerotate;

      if (!translations) {
        translations = {
          rotateRight: "Rotate Clockwise",
          rotateLeft: "Rotate Counter-clockwise"
        }
      }

      if (editor.contextMenu) {
        editor.addMenuItems({
          rotateRight: {
            label: translations.rotateRight,
            icon: this.path + 'icons/rotate-right.png',
            command: 'rotateRight',
            group: 'image',
            order: 1
          },
          rotateLeft: {
            label: translations.rotateLeft,
            icon: this.path + 'icons/rotate-left.png',
            command: 'rotateLeft',
            group: 'image',
            order: 2
          }
        });

        editor.contextMenu.addListener(function (element, selection) {
          var imageElement = element.getAscendant('img', true);
          if (imageElement) {
            return {
              rotateLeft: CKEDITOR.TRISTATE_OFF,
              rotateRight: CKEDITOR.TRISTATE_OFF
            };
          }
        });
      }

    }
  });


  function rotateSelectedImageByAngle(editor, angle) {
    var selection = editor.getSelection();
    var element = selection.getStartElement();
    var imageElement = element.getAscendant('img', true);
    if (!imageElement) {
      editor.showNotification("no image element?", "warning");
      return;
    }
    var domImageElement = imageElement.$;
    if (!domImageElement) {
      editor.showNotification("no DOM image element?", "warning");
      return;
    }

    if ('crossOrigin' in domImageElement) {
      // this will not work if image respond headers will not have Access-Control-Allow-Origin: *
      domImageElement.setAttribute("crossOrigin", "anonymous");
    }

    try {
      rotateByAngle(editor, domImageElement, angle);
    } catch (err) {
      if (err.code === 18) {
        editor.showNotification("Image is from other domain and can't be rotated", "warning");
      }
    }
  }

  function rotateByAngle(editor, imageElement, angle) {
    if(angle != 90 && angle != -90) {
      editor.showNotification("Invalid angle.", "warning");
    }

    const url = imageElement.src.split("?")[0];
    var urlParams = new URLSearchParams(imageElement.src.split("?")[1]);

    if(urlParams.has('rot')) {
      angle += parseInt(urlParams.get('rot'));
    }

    if(angle >= 360) {
      angle = angle % 360;
    }

    if(angle < 0) {
      angle = 360 + angle;
    }

    urlParams.set('rot', angle);

    $.ajax({
      url: url + "?" + urlParams.toString(),
      type: "post",
      success: function( data ) {
        if(data.code) {
          editor.showNotification(data.message, "warning");
        } else {
          imageElement.src = url + "?" + urlParams.toString();
          imageElement.setAttribute("data-cke-saved-src", url + "?" + urlParams.toString());

          // we always rotate by +/- 90°, so we have to flip the width and the height of the image
          var width = imageElement.height;
          var height = imageElement.width;

          imageElement.style.height = height + "px";
          imageElement.style.width = width + "px";
        }
      }
    });
  }

})();