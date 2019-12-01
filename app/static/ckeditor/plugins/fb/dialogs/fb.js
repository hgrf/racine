getStyle = function (el, prop) {
    if (typeof getComputedStyle !== 'undefined') {
        return getComputedStyle(el, null).getPropertyValue(prop);
    } else {
        return el.currentStyle[prop];
    }
};

CKEDITOR.dialog.add( 'fbDialog', function(editor) {
    return {
        title: 'File browser',
        minWidth: 400,
        minHeight: 200,
        buttons: [],
        contents: [
            {
                id: 'tab-basic',
                label: 'Basic Settings',
                elements: [
                    // c.f. https://ckeditor.com/docs/ckeditor4/latest/api/CKEDITOR_dialog_definition_html.html
                    {
                        id: 'fbiframe',
                        type: 'html',
                        style: 'height: 100%;',
                        html: '<iframe style="width:100%"></iframe>'
                    }
                ]
            }
        ],
        onLoad: function() {
            this.on('resize', function() {
                // calculate the height for the iframe to fill the dialog window
                var iframe = document.getElementById(this.getContentElement('tab-basic', 'fbiframe').domId);
                var dialog = this.getElement()['$'];
                var td = dialog.getElementsByClassName('cke_dialog_contents_body')[0];
                //var height = parseInt(getStyle(td, 'height'), 10); // this yields the wrong height in IE11
                var height = parseInt(td.style.height, 10);
                var td2 = td.getElementsByClassName('cke_dialog_ui_vbox_child')[0];
                var pt2 = parseInt(getStyle(td2, 'padding-top'), 10);
                var pb2 = parseInt(getStyle(td2, 'padding-bottom'), 10);
                height -= pt2+pb2+10; // 10 pixels extra because otherwise it somehow doesn't fit
                iframe.style.height = height.toString(10)+'px';

                /* with jQuery:
                var iframe = $(document.getElementById(this.getContentElement('tab-basic', 'fbiframe').domId));
                var element = $(this.getElement()['$']);
                var td = element.find('.cke_dialog_contents_body').first();
                var height = td.height();       // padding already taken into account
                // now subtract vertical padding of .cke_dialog_ui_vbox_child
                td = td.find('.cke_dialog_ui_vbox_child').first();
                height -= td.innerHeight()-td.height()+10; // 10 pixels extra because otherwise it somehow doesn't fit
                iframe.height(height);*/
            });
        },
        onShow: function(event) {
            // check if sample_id is defined or assign default value 0
            var sample_id = typeof sample_id !== 'undefined' ? sample_id : 0;
            var iframe = document.getElementById(this.getContentElement('tab-basic', 'fbiframe').domId);
            // resize the dialog
            this.move(0.1*window.innerWidth, 0.1*window.innerHeight, false);
            this.resize(0.8*window.innerWidth, 0.7*window.innerHeight);
            this.fire('resize');
            // update the iframe content
            iframe.contentWindow.location.href = "/browser?type="+CKEDITOR.fbtype+
                "&upload="+CKEDITOR.fbupload+"&"+(sample_id ? "sample="+sample_id : "");
        }
    };
});