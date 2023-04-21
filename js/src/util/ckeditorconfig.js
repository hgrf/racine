const ckeditorconfig = {
  extraPlugins: 'save,fb,imagerotate',
  imageUploadUrl: '/browser/upload?type=img',
  uploadUrl: '/browser/upload?type=att',
  filebrowserImageUploadUrl: '/browser/upload?type=img',
  filebrowserLinkUploadUrl: '/browser/upload?type=att',
  toolbarGroups: [
    {name: 'clipboard', groups: ['clipboard', 'undo']},
    {name: 'editing', groups: ['find', 'selection', 'spellchecker', 'editing']},
    {name: 'forms', groups: ['forms']},
    {name: 'document', groups: ['mode', 'document', 'doctools']},
    {name: 'others', groups: ['others']},
    {name: 'basicstyles', groups: ['basicstyles', 'cleanup']},
    {name: 'styles', groups: ['styles']},
    {name: 'paragraph', groups: ['list', 'indent', 'blocks', 'align', 'bidi', 'paragraph']},
    {name: 'links', groups: ['links']},
    {name: 'insert', groups: ['insert']},
    {name: 'colors', groups: ['colors']},
    {name: 'about', groups: ['about']},
    {name: 'tools', groups: ['tools']},
  ],
  removeButtons: 'Cut,Copy,Paste,PasteText,PasteFromWord,Undo,Redo,BGColor,RemoveFormat,Outdent,' +
    'Indent,Blockquote,About,Strike,Scayt,Anchor,Source',
};

export default ckeditorconfig;
