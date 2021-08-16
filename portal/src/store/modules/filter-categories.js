import _ from 'lodash'
import { parseSearchMaterialsQuery } from '~/components/_helpers'
import axios from '~/axios'
import router from '~/router'

const PUBLISHER_DATE_ID = 'lom.lifecycle.contribute.publisherdate'

function getFiltersForSearch(items) {
  return _.reduce(
    items,
    (results, item) => {
      // Recursively find selected filters for the children
      if (item.children.length) {
        results = results.concat(getFiltersForSearch(item.children))
      }
      // Add this filter if it is selected
      if (item.selected && !_.isNull(item.parent)) {
        results.push(item)
      }
      // Also add this filter if a date has been selected
      if (
        item.external_id === PUBLISHER_DATE_ID &&
        (item.dates.start_date || item.dates.end_date)
      ) {
        results.push(item)
      }
      return results
    },
    []
  )
}

function getFiltersFromQuery(query) {
  let querySearch = parseSearchMaterialsQuery(query)
  let selected = {}
  if (!_.isEmpty(querySearch.search)) {
    _.forEach(querySearch.search.filters, filter => {
      _.reduce(
        filter.items,
        (obj, item) => {
          obj[item] = true
          return obj
        },
        selected
      )
    })
  }
  return { selected, dateRange: querySearch.dateRange }
}

function loadCategoryFilters(items, selected, dates, opened, showAlls, parent) {
  selected = selected || {}
  dates = _.isEmpty(dates) ? { start_date: null, end_date: null } : dates
  opened = opened || []
  showAlls = showAlls || []
  let searchId = _.isNil(parent) ? null : parent.searchId

  _.forEach(items, item => {
    // Set values that might be relevant when loading children
    item.searchId = searchId || item.external_id
    item.selected = selected[item.external_id] || false
    // Set relevant properties for date filters
    if (item.external_id === PUBLISHER_DATE_ID) {
      item.dates = dates
      item.selected = dates.start_date || dates.end_date
    }
    // Load children and retrospecively set some parent properties
    let hasSelectedChildren = loadCategoryFilters(
      item.children,
      selected,
      dates,
      opened,
      showAlls,
      item
    )
    item.selected = item.selected || hasSelectedChildren
    item.isOpen =
      opened.indexOf(item.id) >= 0 || item.selected || hasSelectedChildren
    item.showAll = showAlls.indexOf(item.id) >= 0
  })
  return _.some(items, item => {
    return item.selected
  })
}

export default {
  state: {
    filter_categories: null,
    filter_categories_loading: null,
    disciplines: null,
    languages: null,
    byCategoryId: {}
  },
  getters: {
    filter_categories(state) {
      return state.filter_categories
    },
    filter_categories_loading(state) {
      return state.filter_categories_loading
    },
    disciplines(state) {
      return state.disciplines
    },
    getCategoryById(state) {
      return itemId => {
        return state.byCategoryId[itemId]
      }
    },
    search_filters(state) {
      if (_.isNil(state.filter_categories)) {
        return []
      }
      let selected = getFiltersForSearch(state.filter_categories.results)
      let selectedGroups = _.groupBy(selected, 'searchId')

      const filterMap = {}
      for (const group in selectedGroups) {
        const items = selectedGroups[group].map(item => {
          return item.external_id
        })
        filterMap[group] = items
      }
      return filterMap
    },
    getFiltersFromQuery() {
      return getFiltersFromQuery
    }
  },
  actions: {
    async getFilterCategories({ state, commit }) {
      if (
        _.isNil(state.filter_categories_loading) &&
        _.isEmpty(state.filter_categories)
      ) {
        const promise = axios.get('filter-categories/').then(({ data }) => {
          // Preprocess the filters
          data.defaults = _.cloneDeep(data)
          let filters = getFiltersFromQuery(router.currentRoute.query)
          loadCategoryFilters(data, filters.selected, filters.dateRange)

          commit('SET_FILTER_CATEGORIES', data)
          commit('SET_FILTER_CATEGORIES_LOADING', null)
          return data
        })
        commit('SET_FILTER_CATEGORIES_LOADING', promise)
      }

      return _.isNil(state.filter_categories_loading)
        ? state.filter_categories
        : state.filter_categories_loading
    }
  },
  mutations: {
    SET_FILTER_CATEGORIES(state, payload) {
      if (_.isNil(payload)) {
        return
      }

      state.filter_categories = payload

      const disciplines = payload.find(
        child => child.external_id.search('discipline.id') !== -1
      )
      state.disciplines = _.reduce(
        disciplines.children,
        (obj, value) => {
          obj[value.external_id] = value
          return obj
        },
        {}
      )

      state.byCategoryId = {}
      function setCategoryIds(items) {
        _.forEach(items, item => {
          state.byCategoryId[item.external_id] = item
          setCategoryIds(item.children)
        })
      }
      setCategoryIds(payload)
    },
    SET_FILTER_CATEGORIES_LOADING(state, payload) {
      state.filter_categories_loading = payload
    }
  }
}
