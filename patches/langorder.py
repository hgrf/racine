import json

order = [
    "editor",
    "editorPanel",
    "common",
    "about",
    "basicstyles",
    "blockquote",
    "notification",
    "button",
    "toolbar",
    "clipboard",
    "contextmenu",
    "elementspath",
    "filetools",
    "format",
    "horizontalrule",
    "image",
    "indent",
    "list",
    "magicline",
    "maximize",
    "pastetext",
    "pastefromword",
    "removeformat",
    "sourcearea",
    "specialchar",
    "scayt",
    "stylescombo",
    "table",
    "undo",
    "widget",
    "uploadwidget",
    "wsc",
    "colorbutton",
    "fakeobjects",
    "link",
]

with open("app/static/ckeditor/lang/en.js", "r") as f:
    data = f.read()
    data = data.split("=", 1)[1]
    data = data[:-1]
    data = json.loads(data)

    data_new = {}
    for key in order:
        data_new[key] = data[key]

    with open("app/static/ckeditor/lang/en.js", "wb") as fout:
        fout.write(b"\xef\xbb\xbf")
        fout.write(
            b"""/*
Copyright (c) 2003-2018, CKSource - Frederico Knabben. All rights reserved.
For licensing, see LICENSE.md or http://ckeditor.com/license
*/
CKEDITOR.lang['en']="""
        )
        fout.write(json.dumps(data_new, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
        fout.write(b";")
