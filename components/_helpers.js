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

export const generateSearchMaterialsQuery = (
  data = { filters: [], search_text: [] }
) => {
  return {
    path: '/materials/search/',
    query: Object.assign({}, data, {
      filters: JSON.stringify(data.filters),
      search_text: JSON.stringify(data.search_text)
    })
  };
};
