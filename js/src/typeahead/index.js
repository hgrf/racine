module.exports = {
  'Bloodhound': require('./bloodhound.js'),
  'loadjQueryPlugin': function() {
    require('./typeahead.bundle.js');
  },
};
