// parse the query string and put it in a dictionary
var queryDict = {};
location.search.substr(1).split("&").forEach(function(item) {queryDict[item.split("=")[0]] = item.split("=")[1]})

function update_sample_image_and_quit(uploadurl) {
    $.ajax({
        url: "/changesampleimage",
        type: "post",
        data: { "id": queryDict['sample'], "value": data.uploadurl },
            success: function(data) {
            window.opener.location.href = "/sample/"+queryDict['sample'];   // reload the sample page in the editor window
            window.close();     // close the browser window
        }
    });
}

function init_browser() {
    $('#uploadform').attr('action', '/browser/upload?'+location.search.substr(1));


    $('.folder').click( function(event) {
        location.href = "/browser"+"/"+$(this).data('url')+'?'+location.search.substr(1);
        event.preventDefault();
    });

    $('.file').click( function(event) {
        src = $(this).find('img').attr('src')
        if(src == '/static/file.png') {
            alert('Please choose a file with a valid extension.');
            return;
        }
        $.ajax({
            url: "/browser/savefromsmb",
            type: "post",
            data: { "src": src },
            success: function(data) {
                terminate_browser(data.uploadurl)
            }
        });
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