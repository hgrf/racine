import $ from 'jquery';

import R from '../../racine';
import {updateNavCaret} from './navcarets';

function draggableHandlers(activeEntry) {
  return {
    dragstart: function(event) {
      const id = $(event.target).data('id');
      const name = $(event.target).data('name');
      event.originalEvent.dataTransfer.setData('sampleid', id);
      event.originalEvent.dataTransfer.setData('text/html', `<a href="/sample/${id}">${name}</a>`);
    },
    drop: function(event) {
    // reset background color (but highlight if sample is active)
      $(this).css('background-color', 'transparent');
      activeEntry.css('background-color', '#BBBBFF');
    },
  };
};

function dropZoneHandlers(activeEntry) {
  return {
    dragenter: function(event) {
      event.preventDefault();
      event.stopPropagation();
    },
    dragover: function(event) {
      $(this).css('background-color', '#CCCCEE');
      event.preventDefault();
      event.stopPropagation();
    },
    dragleave: function(event) {
    // reset background color (but highlight if sample is active)
      $(this).css('background-color', 'transparent');
      activeEntry.css('background-color', '#BBBBFF');
    },
    drop: function(event) {
      const draggedId = parseInt(event.originalEvent.dataTransfer.getData('sampleid'));
      const parentId = parseInt($(this).data('id'));
      event.preventDefault();
      event.stopPropagation();

      // reset background color (but highlight if sample is active)
      $(this).css('background-color', 'transparent');
      activeEntry.css('background-color', '#BBBBFF');

      if (draggedId === parentId) return;

      R.samplesAPI.changeParent(draggedId, parentId, function(error, data, response) {
        if (!response) {
          R.errorDialog('Server error. Please check your connection.');
        } else if (response.error) {
          if (response.body.message) {
            R.errorDialog(response.body.message);
          } else {
            R.errorDialog(response.error);
          }
        } else {
          const draggedItem = $('#nav-container'+draggedId);
          const oldParent = draggedItem.parent().prev();
          if (parentId !== 0) {
          // moving to a regular nav-entry
            draggedItem.appendTo('#nav-children'+parentId);
            updateNavCaret($('#nav-entry'+parentId));
          } else {
          // moving to root
            draggedItem.appendTo('#nav-mysamples');
          }
          // if it's not the root entry, update the caret
          if (oldParent.length) {
            updateNavCaret(oldParent);
          }
        }
      });
    },
  };
};

export {draggableHandlers, dropZoneHandlers};
