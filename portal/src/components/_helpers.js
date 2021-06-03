import i18n from '~/i18n'

export const generateSearchMaterialsQuery = function(
  data = { filters: {}, search_text: '' },
  name = 'materials-search'
) {
  name += '___' + i18n.locale

  return {
    name: name,
    query: {
      ...data,
      filters: JSON.stringify(data.filters),
      search_text: JSON.stringify(data.search_text)
    }
  }
}

export const parseSearchMaterialsQuery = function(query) {
  let search = { search_text: '', filters: {} }

  if (query) {
    search = {
      ...query,
      filters: query.filters ? parseFilters(query.filters) : {},
      search_text: query.search_text ? parseSearchText(query.search_text) : ''
    }
  }

  const dateRangeItems =
    search.filters['lom.lifecycle.contribute.publisherdate'] || []
  const dateRange = {
    start_date: dateRangeItems[0],
    end_date: dateRangeItems[1]
  }

  return { search, dateRange }
}

const parseFilters = function(filters) {
  const parsedFilters = JSON.parse(filters)
  if (Array.isArray(parsedFilters)) {
    return parsedFilters.reduce((memo, filter) => {
      if (filter.external_id) {
        memo[filter.external_id] = filter.items
      }

      return memo
    }, {})
  }

  return parsedFilters
}

const parseSearchText = function(searchText) {
  const parsedSearchText = JSON.parse(searchText)
  if (Array.isArray(parsedSearchText)) {
    return parsedSearchText[0]
  }

  return parsedSearchText
}

export const validateHREF = function(href) {
  return href.search(process.env.frontendUrl) === 0
    ? href
    : process.env.frontendUrl
}
