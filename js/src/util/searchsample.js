import R from '../racine';
import $ from 'jquery';
import {Bloodhound} from '../typeahead';

const samples = new Bloodhound({
  datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
  queryTokenizer: Bloodhound.tokenizers.whitespace,
  remote: {
    url: '/aview/search?autocomplete&term=%QUERY',
    wildcard: '%QUERY',
    transform: function(data) {
      return data.results;
    },
  },
});

function createSearchSample(searchfield) {
  searchfield.typeahead({
    minLength: 1,
    highlight: true,
  }, {
    name: 'samples',
    display: function(result) {
      return result.name;
    },
    source: samples,
    templates: {
      suggestion: function(result) {
        let parentinfo;
        let ownerinfo;
        if (result.parentname != '') {
          parentinfo =
            '<span style="white-space:nowrap;">' +
              `<i class="${R.icons.childItem}"></i>` +
              '&nbsp;' + result.parentname +
            '</span>\n';
        } else {
          parentinfo = '';
        }
        if (!result.mysample) {
          ownerinfo =
            '<span style="white-space:nowrap;">' +
              `<i class="${R.icons.user}"></i>` +
              '&nbsp;' + result.ownername +
            '</span>\n';
        } else {
          ownerinfo = '';
        }
        return (
          '<div style="padding-left:2em;padding-bottom:0.5em;padding-top:0.5em;">\n' +
            '<span style="white-space:nowrap;">' +
              '<img src="/static/images/sample.png" ' +
                'style="margin-left:-1.5em;width:1.5em;height:1.5em;">' +
              '&nbsp;' + result.name +
            '</span>\n' +
            ownerinfo +
            parentinfo +
          '</div>'
        );
      },
    },
  });
}

function createSelectSample(searchfield, hiddenfield, valid=true, placeholder='None') {
  searchfield.wrap('<div class="input-group"></div>');
  searchfield.attr('placeholder', placeholder);

  const commonClass = R.icons.selectSample.common;
  const iconOk = R.icons.ok;
  const iconAlert = R.icons.alert;

  const indicatorspan = $('<span class="input-group-text"></span>');
  const indicator = $('<i class="'+(valid?iconOk:iconAlert)+commonClass+
                      '" style="color:'+(valid?'green':'red')+';"></i>');
  indicatorspan.append(indicator);
  searchfield.after(indicatorspan);

  searchfield.markvalid = function() {
    hiddenfield.attr('value', '');
    indicator.removeClass(iconAlert);
    indicator.addClass(iconOk);
    indicator.css('color', 'green');
  };

  searchfield.markinvalid = function() {
    hiddenfield.attr('value', -1);
    indicator.removeClass(iconOk);
    indicator.addClass(iconAlert);
    indicator.css('color', 'red');
  };

  searchfield.on('input', function() {
    if (searchfield.val() == '') {
      searchfield.markvalid();
    } else {
      searchfield.markinvalid();
    }
  });

  searchfield.bind('typeahead:select', function(ev, suggestion) {
    hiddenfield.attr('value', suggestion.id);
    indicator.removeClass(iconAlert);
    indicator.addClass(iconOk);
    indicator.css('color', 'green');
  });

  createSearchSample(searchfield);
}

export {createSearchSample, createSelectSample};
