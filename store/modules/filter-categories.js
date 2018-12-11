export default {
  state: {
    filter_categories: null,
    filter_categories_loading: null,
    disciplines: null,
    educationallevels: null
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
    }
  },
  actions: {
    async getFilterCategories({ state, commit }) {
      if (!state.filter_categories && !state.filter_categories_loading) {
        commit('SET_FILTER_CATEGORIES_LOADING', true);
        const filter = await this.$axios.$get('filter-categories/');
        commit('SET_FILTER_CATEGORIES', filter);
        commit('SET_FILTER_CATEGORIES_LOADING', false);

        return state.filter_categories;
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
    },
    SET_FILTER_CATEGORIES_LOADING(state, payload) {
      state.filter_categories_loading = payload;
    }
  }
};
