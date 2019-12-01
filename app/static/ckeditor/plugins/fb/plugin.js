// c.f. https://ckeditor.com/docs/ckeditor4/latest/guide/plugin_sdk_sample_1.html
CKEDITOR.plugins.add('fb', {
    init: function(editor) {
        editor.addCommand( 'fb', new CKEDITOR.dialogCommand('fbDialog'));

        CKEDITOR.dialog.add('fbDialog', this.path+'dialogs/fb.js');

        CKEDITOR.fbtype = 'img';   // by default, only accept image selection (the other option is 'att' for attachment)
        CKEDITOR.fbupload = false; // by default, disable upload in file browser
        CKEDITOR.fbcallback = function() { console.warn('The file browser call back has not been set up.') };
    }
});