import _ from 'lodash';


const PUBLISHER_DATE_ID = 'lom.lifecycle.contribute.publisherdate';


function getFiltersForSearch(items) {
  return _.reduce(items, (results, item) => {
    // Recursively find selected filters for the children
    if(item.children.length) {
      results = results.concat(getFiltersForSearch(item.children));
    }
    // Add this filter if it is selected
    if(item.selected && !_.isNull(item.parent)) {
      results.push(item);
    }
    // Also add this filter if a date has been selected
    if(item.external_id === PUBLISHER_DATE_ID && (item.dates.start_date || item.dates.end_date)) {
      results.push(item);
    }
    return results;
  }, []);
}


function loadCategoryFilters(items, parent) {

  let parentSelected = (_.isNull(parent)) ? false : parent.selected || parent.enabled_by_default;
  let searchId = (_.isNull(parent)) ? null : parent.searchId;
  _.forEach(items, (item) => {

    // Set relevant properties for date filters
    if(item.external_id === PUBLISHER_DATE_ID) {
      item.dates = {
        start_date: null,
        end_date: null
      }
    }
    // Set values that might be relevant when loading children
    item.searchId = searchId || item.external_id;
    item.selected = parentSelected || item.enabled_by_default;
    // Load children and retrospecively set some parent properties
    let hasSelectedChildren = loadCategoryFilters(item.children, item);
    item.show_all = false;
    item.selected = item.isOpen = item.selected || hasSelectedChildren;

  });
  return _.some(items, (item) => { return item.selected; });

}

export default {
  state: {
    filter_categories: null,
    filter_categories_loading: null,
    disciplines: null,
    educationallevels: null,
    languages: null,
    all_educationallevels: {
      external_id: 'lom.classification.obk.educationallevel.id',
      items: [
        'be140797-803f-4b9e-81cc-5572c711e09c',
        'f33b30ee-3c82-4ead-bc20-4255be9ece2d',
        'de952b8b-efa5-4395-92c0-193812130c67',
        'f3ac3fbb-5eae-49e0-8494-0a44855fff25',
        'a598e56e-d1a6-4907-9e2c-3da64e59f9ae',
        '00ace3c7-d7a8-41e6-83b1-7f13a9af7668',
        '654931e1-6f8b-4f72-aa4b-92c99c72c347',
        '8beca7eb-95a5-4c7d-9704-2d2a2fc4bc65',
        'bbbd99c6-cf49-4980-baed-12388f8dcff4',
        '18656a7c-95a5-4831-8085-020d3151aceb',
        '2998f2e0-449d-4911-86a2-f4cbf1a20b56'
      ]
    }
  },
  getters: {
    filter_categories(state) {
      return state.filter_categories;
    },
    filter_categories_loading(state) {
      return state.filter_categories_loading;
    },
    disciplines(state) {
      return state.disciplines;
    },
    educationallevels(state) {
      return state.educationallevels;
    },
    all_educationallevels(state) {
      return state.all_educationallevels;
    },
    languages(state) {
      return state.languages;
    },
    search_filters(state) {

      if(_.isNil(state.filter_categories)) {
        return []
      }

      let selected = getFiltersForSearch(state.filter_categories.results);
      let selectedGroups = _.groupBy(selected, 'searchId');
      return _.map(selectedGroups, (items, group) => {
        if(group === PUBLISHER_DATE_ID) {
          let dates = items[0].dates;
          return {
            external_id: group,
            items: [dates.start_date || null, dates.end_date || null]
          }
        }
        return {
          external_id: group,
          items: _.reject(
            _.map(items, 'external_id'),
            _.isEmpty
          )
        }
      });

    }
  },
  actions: {
    async getFilterCategories({ state, commit }) {

      if (_.isNil(state.filter_categories_loading) && _.isEmpty(state.filter_categories)) {
        let promise = this.$axios.get('filter-categories/').then((response) => {

          // Preprocess the filters
          loadCategoryFilters(response.data.results, null);

          commit('SET_FILTER_CATEGORIES', response.data);
          commit('SET_FILTER_CATEGORIES_LOADING', null);
          return response.data;
        });
        commit('SET_FILTER_CATEGORIES_LOADING', promise);
      }

      return _.isNil(state.filter_categories_loading) ? state.filter_categories : state.filter_categories_loading;
    }
  },
  mutations: {
    SET_FILTER_CATEGORIES(state, payload) {
      state.filter_categories = payload;
      const disciplines = payload.results.find(
        child => child.external_id.search('discipline.id') !== -1
      );
      state.disciplines = Object.assign({}, disciplines, {
        items: disciplines.children.reduce((prev, next) => {
          prev[next.external_id] = next;
          return prev;
        }, {})
      });
      const educationallevels = payload.results.find(
        child => child.external_id.search('educationallevel.id') !== -1
      );
      state.educationallevels = Object.assign({}, educationallevels, {
        items: educationallevels.children.reduce((prev, next) => {
          prev[next.external_id] = next;
          return prev;
        }, {})
      });
      const languages = payload.results.find(
        item => item.external_id.search('lom.general.language') !== -1
      );
      state.languages = Object.assign({}, languages);
    },
    SET_FILTER_CATEGORIES_LOADING(state, payload) {
      state.filter_categories_loading = payload;
    }
  }
};
