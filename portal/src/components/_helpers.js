import i18n from '~/i18n'
import { isEmpty } from 'lodash'

export const generateSearchMaterialsQuery = function (
  data = { filters: {}, search_text: '' },
  name = 'materials-search'
) {
  if (name.indexOf('___') < 0) {
    name += '___' + i18n.locale
  }

  return {
    name: name,
    query: {
      ...data,
      filters: JSON.stringify(data.filters),
      search_text: JSON.stringify(data.search_text),
    },
  }
}

export const parseSearchMaterialsQuery = function (query) {
  let search = { search_text: '', filters: {} }

  if (query) {
    search = {
      ...query,
      filters: query.filters ? parseFilters(query.filters) : {},
      search_text: query.search_text ? parseSearchText(query.search_text) : '',
    }
  }

  const dateRangeItems = search.filters['publisher_date'] || []
  const dateRange = {
    start_date: dateRangeItems[0],
    end_date: dateRangeItems[1],
  }

  return { search, dateRange }
}

const parseFilters = function (filters) {
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

const parseSearchText = function (searchText) {
  const parsedSearchText = JSON.parse(searchText)
  if (Array.isArray(parsedSearchText)) {
    return parsedSearchText[0]
  }

  return parsedSearchText
}

export const validateHREF = function (href) {
  return href.search(process.env.frontendUrl) === 0
    ? href
    : process.env.frontendUrl
}

export const addFilter = function (search, category, filterId) {
  if (isEmpty(search.filters[category])) {
    search.filters[category] = [filterId]
    return search
  } else if (search.filters[category].indexOf(filterId) >= 0) {
    return search
  }
  search.filters[category].push(filterId)
  return search
}
