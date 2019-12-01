// parse the query string and put it in a dictionary
var queryDict = {};
location.search.substr(1).split("&").forEach(function(item) {queryDict[item.split("=")[0]] = item.split("=")[1]})

function init_browser() {
    // tell the upload form how to communicate with the server
    $('#uploadform').submit(function(event) {
        event.preventDefault();
        var formData = new FormData(this);

        // show "activity" overlay
        $('#overlaytext').text('Uploading file...');
        $('#overlay').css("display", "block");
        // send file to server
        $.ajax({
            url: '/browser/upload?type=img',
            data: formData,
            type: 'POST',
            contentType: false,
            processData: false,
            success: function(data) {
                if(data.uploaded) {
                    parent.CKEDITOR.dialog.getCurrent().hide();	// hide the file browser
                    parent.CKEDITOR.fbcallback(data.url); // call the call back
                } else {
                    alert("Error: "+data.error['message']);
                    $('#overlay').css("display", "none");
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                alert("Error when communicating with server.");
            }
        });
    });

    function folderclickhandler(event) {
        location.href = "/browser/" + $(this).data('url') + '?' + location.search.substr(1);
        event.preventDefault();
    }

    $('.folder').click(folderclickhandler);

    $('.file').click( function(event) {
        path = $(this).data('path');
        // show "activity" overlay
        $('#overlaytext').text('Saving file...');
        $('#overlay').css("display", "block");
        // tell the server to store the file
        $.ajax({
            url: "/browser/savefromsmb",
            type: "post",
            data: { "path": path,
                    "type": queryDict['type'] },
            success: function(data) {
                if(data.code) {
                    alert("Error: "+data.message);
                    $('#overlay').css("display", "none");
                } else {
                    // hide the file browser
                    parent.CKEDITOR.dialog.getCurrent().hide();
                    // call the call back function
                    parent.CKEDITOR.fbcallback(data.uploadurl, {'filename': data.filename, 'type': data.type});
                }
            }
        });
    });

    // TODO: note that the functionality of inpectpath and inspectresource could be easily combined and the following
    // code could be reduced a lot by treating historyitem, resource and shortcut all the same way...

    // check for each history item if it is available
    $('.historyitem').each(function(index, element) {
        var historyitemdiv = $(this);
        $.ajax({
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
       $.ajax({
           url: "/browser/inspectresource",
           type: "post",
           data: { "sampleid": queryDict['sample'],
                   "resourceid": $(this).data('id') },
           success: function(data) {
               resourcediv = $('#resource' + data.resourceid);
               shortcutsdiv = $('#shortcuts' + data.resourceid);
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
           }
       })
    });
}

$(document).ready(function() {
    init_browser();
});