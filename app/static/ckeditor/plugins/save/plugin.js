/**
 * @license Copyright (c) 2003-2018, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see LICENSE.md or https://ckeditor.com/legal/ckeditor-oss-license
 *
 * modified by Holger Graef to work in inline mode
 * close button by hendr1x: https://ckeditor.com/addon/closebtn
 * http://stackoverflow.com/questions/18956257/how-to-add-an-ajax-save-button-with-loading-gif-to-ckeditor-4-2-1-working-samp
 */

/**
 * @fileOverview The Save plugin.
 */

( function() {
	var saveCmd = {
		exec: function( editor ) {
			editor.fire('done', 'save')
		}
	};

	var closeCmd = {
		exec : function(editor) {
			editor.fire('done', 'abort');
        }
	}

	var pluginName = 'save';

	// Register a plugin named "save".
	CKEDITOR.plugins.add( pluginName, {
		// jscs:disable maximumLineLength
		lang: 'af,ar,az,bg,bn,bs,ca,cs,cy,da,de,de-ch,el,en,en-au,en-ca,en-gb,eo,es,es-mx,et,eu,fa,fi,fo,fr,fr-ca,gl,gu,he,hi,hr,hu,id,is,it,ja,ka,km,ko,ku,lt,lv,mk,mn,ms,nb,nl,no,oc,pl,pt,pt-br,ro,ru,si,sk,sl,sq,sr,sr-latn,sv,th,tr,tt,ug,uk,vi,zh,zh-cn', // %REMOVE_LINE_CORE%
		// jscs:enable maximumLineLength
		icons: 'save,closebtn',
		hidpi: true,
		init: function( editor ) {
			// Save plugin is for inline mode only.
			if ( editor.elementMode != CKEDITOR.ELEMENT_MODE_INLINE )
				return;

			editor.addCommand( 'save', saveCmd );
			editor.addCommand( 'closetoolbar', closeCmd );

			editor.ui.addButton( 'save', {
				label: editor.lang.save.toolbar,
				command: 'save',
				toolbar: 'document,0'
			});

			editor.ui.addButton( 'closebtn', {
				label: 'Close',
				command: 'closetoolbar',
			    toolbar: 'tools,0'
			});
		}
	} );
} )();