// c.f. https://ckeditor.com/docs/ckeditor4/latest/guide/plugin_sdk_sample_1.html
var launchfb = {
    exec: function( editor ) {
        CKEDITOR.fbtype = 'auto';
        CKEDITOR.fbcallback = function(url, data) {
            if(data.type === 'img')
                editor.insertHtml('<img src="'+url+'" width="400">');
            else if(data.type === 'att')
                editor.insertHtml('<a href="'+url+'">'+data.filename+'</a>')

        };
        editor.execCommand('fb');
    }
};

CKEDITOR.plugins.add('fb', {
    icons: 'fb',
    hidpi: true,
    init: function(editor) {
        editor.addCommand( 'fb', new CKEDITOR.dialogCommand('fbDialog'));
        editor.addCommand( 'launchfb', launchfb );
        editor.ui.addButton( 'fb', {
            label: 'File browser',
            command: 'launchfb',
            toolbar: 'insert,1'
        });

        CKEDITOR.dialog.add('fbDialog', this.path+'dialogs/fb.js');

        CKEDITOR.fbtype = 'img';   // by default, only accept image selection (the other option is 'att' for attachment)
        CKEDITOR.fbupload = false; // by default, disable upload in file browser
        CKEDITOR.fbcallback = function() { console.warn('The file browser call back has not been set up.') };
    }
});