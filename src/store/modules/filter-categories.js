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
    }
  },
  actions: {
    async getFilterCategories({ state, commit }) {
      if (!state.filter_categories && !state.filter_categories_loading) {
        commit('SET_FILTER_CATEGORIES_LOADING', true);
        const filter = await this.$axios.$get('filter-categories/');
        commit('SET_FILTER_CATEGORIES', filter);
        commit('SET_FILTER_CATEGORIES_LOADING', false);

        return filter;
      }
      return state.filter_categories;
    }
  },
  mutations: {
    SET_FILTER_CATEGORIES(state, payload) {
      state.filter_categories = payload;
      const disciplines = payload.results.find(
        item => item.external_id.search('discipline.id') !== -1
      );
      state.disciplines = Object.assign({}, disciplines, {
        items: disciplines.items.reduce((prev, next) => {
          prev[next.external_id] = next;
          return prev;
        }, {})
      });
      const educationallevels = payload.results.find(
        item => item.external_id.search('educationallevel.id') !== -1
      );
      state.educationallevels = Object.assign({}, educationallevels, {
        items: educationallevels.items.reduce((prev, next) => {
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
