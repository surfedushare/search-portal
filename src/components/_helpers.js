import _ from 'lodash';


export const debounce = function(func, wait, immediate) {
  var timeout;
  return function() {
    var context = this,
      args = arguments;
    var later = function() {
      timeout = null;
      if (!immediate) func.apply(context, args);
    };
    var callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow) func.apply(context, args);
  };
};

export const generateSearchMaterialsQuery = function(data = { filters: [], search_text: [] }, name = 'materials-search') {

  const filters = data.filters ? data.filters.filter(item => Object.keys(item).length) : [];
  name += '___' + this.$i18n.locale;

  return {
    name: name,
    query: Object.assign({}, data, {
      filters: JSON.stringify(filters),
      search_text: JSON.stringify(data.search_text)
    })
  };
};

export const parseSearchMaterialsQuery = function(query) {
  let search = { search_text: [], filters: [] };
  if(!_.isEmpty(query)) {
    search = Object.assign({}, query, {
      filters: query.filters ? JSON.parse(query.filters) : [],
      search_text: query.search_text ? JSON.parse(query.search_text) : []
    });
  }

  const publisherDate = search.filters.find(item => item.external_id === 'lom.lifecycle.contribute.publisherdate');
  let dateRange = {};
  if (publisherDate && publisherDate.items) {
    dateRange = {
      start_date: publisherDate.items[0] || null,
      end_date: publisherDate.items[1] || null
    };
  }
  return {search, dateRange}
};

export const validateHREF = function(href) {
  return href.search(process.env.frontendUrl) === 0
    ? href
    : process.env.frontendUrl;
};
