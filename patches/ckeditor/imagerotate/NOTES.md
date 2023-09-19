We could simply rotate the images by modifying their CSS (e.g. `transform: rotate(90deg);`). However, this
would entail several problems:

* the CSS would also have to be applied when we open lightbox
* the CSS could not be applied when we click on the HD button
* the CSS would have to be applied if the editor is re-opened (see
  https://ckeditor.com/docs/ckeditor4/latest/guide/dev_advanced_content_filter.html)
* setting the correct height of the element is tricky, see
  https://stackoverflow.com/questions/16301625/rotated-elements-in-css-that-affect-their-parents-height-correctly

That's why we decided to rotate the images on the server, even if this is probably not the most efficient and elegant
solution.   
