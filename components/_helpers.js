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

export const generateSearchMaterialsQuery = function(data = { filters: [], search_text: [] }, path = '/materials/search/') {

  const filters = data.filters
    ? data.filters.filter(item => Object.keys(item).length)
    : [];

  if (this && this.$i18n.locale !== 'nl') {
    path = `/${this.$i18n.locale}${path}`;
  }

  return {
    path: path,
    query: Object.assign({}, data, {
      filters: JSON.stringify(filters),
      search_text: JSON.stringify(data.search_text)
    })
  };
};

export const validateHREF = function(href) {
  return href.search(process.env.prodBaseUrl) === 0
    ? href
    : process.env.prodBaseUrl;
};
