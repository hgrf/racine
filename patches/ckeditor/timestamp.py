with open("app/static/ckeditor/skins/moono-lisa/editor.css", "rb") as f:
    data = bytearray(f.read())

    i, j = 0, 0
    while i >= 0:
        i = data.find(b".png?t=", j)
        j = data.find(b")", i)

        data[i:j] = b".png?t=95e5d83"

    with open("app/static/ckeditor/skins/moono-lisa/editor.css", "wb") as fout:
        fout.write(data)
