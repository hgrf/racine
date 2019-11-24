// parse the query string and put it in a dictionary
var queryDict = {};
location.search.substr(1).split("&").forEach(function(item) {queryDict[item.split("=")[0]] = item.split("=")[1]})

function update_sample_image_and_quit(uploadurl) {
    $.ajax({
        url: "/set/sample/image/"+queryDict['sample'],
        type: "post",
        data: { "value": uploadurl },
            success: function(data) {
            window.opener.location.href = "/sample/"+queryDict['sample'];   // reload the sample page in the editor window
            window.close();     // close the browser window
        }
    });
}


function init_browser() {
    // tell the upload form how to communicate with the server (this has to preserve the query string, so that
    // sample and CKEditorFuncNum information is kept)
    $('#uploadform').attr('action', '/browser/upload?caller=msmb&type=img&'+location.search.substr(1));

    function folderclickhandler(event) {
        location.href = "/browser/" + $(this).data('url') + '?' + location.search.substr(1);
        event.preventDefault();
    }

    $('.folder').click(folderclickhandler);

    $('.file').click( function(event) {
        src = $(this).find('img').attr('src')
        if(src == '/static/images/file.png') {
            alert('Please choose a file with a valid extension.');
            return;
        }
        // show "activity" overlay
        $('#overlay').css("display", "block");
        // tell the server to store the file
        $.ajax({
            url: "/browser/savefromsmb",
            type: "post",
            data: { "src": src },
            success: function(data) {
                if(data.code) {
                    alert("Error: "+data.message);
                }
                else {
                    terminate_browser(data.uploadurl);
                }
            }
        });
    });

    // check for each history item if it is available
    $('.historyitem').each(function(index, element) {
        var historyitemdiv = $(this);
        async_api_call({
           url: "/browser/inspectpath",
           type: "post",
           data: { "smbpath": $(this).data('url') },
           success: function(data) {
               if(!data.code) {
                    historyitemdiv.find('img').attr('src', '/static/images/folder.png');
                    historyitemdiv.addClass('available');   // for CSS :hover
                    // add click handler for new elements
                    historyitemdiv.click(folderclickhandler);
               } else {
                    historyitemdiv.find('img').attr('src', '/static/images/folder_inaccessible.png');
               }
           }
        });
    });

    // check for each resource if it is available and if it has a user/sample folder
    $('.resource').each(function(index, element) {
        async_api_call({
           url: "/browser/inspectresource",
           type: "post",
           data: { "sampleid": queryDict['sample'],
                   "resourceid": $(this).data('id') },
           success: function(data, textStatus, jqXHR) {
               var resourcediv = $('#resource' + data.resourceid);
               var shortcutsdiv = $('#shortcuts' + data.resourceid);
               shortcutsdiv.empty();
               if(!data.code) {
                   if(data.userfolder != '') {
                       shortcutsdiv.append("<img class='shortcut' src='/static/images/user.png' data-url='"+data.userfolder+"'>");
                   }
                   if(data.samplefolder != '') {
                       shortcutsdiv.append("<img class='shortcut' src='/static/images/sample.png' data-url='"+data.samplefolder+"'>");
                   }
                   resourcediv.addClass('available'); // for CSS :hover

                   // add click handler for new elements
                   resourcediv.click(folderclickhandler);
                   shortcutsdiv.children('img').click(folderclickhandler);
               } else {
                   resourcediv.append(" (N/A)");
               }
           }});
    });
}

function terminate_browser(uploadurl) {
    if (queryDict['CKEditorFuncNum'] == undefined) {
        // in this case the browser was opened by the sample editor with the intention to change the
        // sample image, so we should do that now:
        update_sample_image_and_quit(uploadurl);
    } else {
        // in this case the browser was opened by a CKEditor and we should inform it
        // about the chosen image
        window.opener.CKEDITOR.tools.callFunction(queryDict['CKEditorFuncNum'], uploadurl);
        window.close();
    }
}